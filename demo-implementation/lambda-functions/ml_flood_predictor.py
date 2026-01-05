#!/usr/bin/env python3
"""
ML Flood Predictor Lambda Function
Uses machine learning to predict flood probability
"""

import json
import boto3
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal

# Global model variable for caching
model = None
feature_columns = None

def load_model():
    """Load ML model from S3 (cached)"""
    global model, feature_columns
    
    if model is None:
        try:
            import joblib
            s3 = boto3.client('s3')
            
            # Get account ID for bucket name
            sts = boto3.client('sts')
            account_id = sts.get_caller_identity()['Account']
            bucket_name = f'flood-prediction-models-{account_id}'
            
            # Download model from S3
            s3.download_file(bucket_name, 
                            'models/flood_prediction_model.joblib', 
                            '/tmp/model.joblib')
            
            # Download feature list
            s3.download_file(bucket_name,
                            'models/model_features.json',
                            '/tmp/features.json')
            
            model = joblib.load('/tmp/model.joblib')
            
            with open('/tmp/features.json', 'r') as f:
                feature_columns = json.load(f)
                
        except Exception as e:
            print(f"Could not load ML model: {e}")
            # Use simple threshold model as fallback
            model = "threshold"
            feature_columns = []
    
    return model, feature_columns

def get_recent_data():
    """Get recent USGS and NOAA data for prediction"""
    dynamodb = boto3.resource('dynamodb')
    
    # Get recent USGS data (last 24 hours)
    usgs_table = dynamodb.Table('FloodGaugeReadings')
    noaa_table = dynamodb.Table('WeatherObservations')
    
    # Query for Chain Bridge gauge (01646500)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    
    # Simplified - in production would do proper time-based queries
    usgs_response = usgs_table.scan(
        FilterExpression='gauge_id = :gauge_id',
        ExpressionAttributeValues={':gauge_id': '01646500'}
    )
    
    noaa_response = noaa_table.scan(
        FilterExpression='station_id = :station_id',
        ExpressionAttributeValues={':station_id': 'KDCA'}
    )
    
    return usgs_response['Items'], noaa_response['Items']

def create_features(usgs_data, noaa_data):
    """Create ML features from recent data"""
    
    # Sort by timestamp
    usgs_sorted = sorted(usgs_data, key=lambda x: x['timestamp'])
    noaa_sorted = sorted(noaa_data, key=lambda x: x['timestamp'])
    
    if not usgs_sorted or not noaa_sorted:
        # Return default features if no data
        return np.array([[5.0, 4.8, 4.5, 0.2, 0.5, 0.1, 0.3, 0.8, 0.5, 12, 180, 6]])
    
    # Get latest readings
    latest_usgs = usgs_sorted[-1]
    latest_noaa = noaa_sorted[-1]
    
    # Create feature vector (simplified)
    features = [
        float(latest_usgs.get('water_level', 5.0)),
        float(latest_usgs.get('water_level', 5.0)) - 0.2,  # lag_1h (simplified)
        float(latest_usgs.get('water_level', 5.0)) - 0.5,  # lag_6h (simplified)
        0.2,  # water_level_change_1h (would calculate from historical)
        0.5,  # water_level_change_6h (would calculate from historical)
        float(latest_noaa.get('precipitation_1hr', 0.1)),
        0.3,  # precip_cumulative_6h (would calculate)
        0.8,  # precip_cumulative_24h (would calculate)
        float(latest_noaa.get('precipitation_forecast_24hr', 0.5)),
        datetime.now().hour,
        datetime.now().timetuple().tm_yday,
        datetime.now().month
    ]
    
    return np.array([features])

def predict_flood_probability(usgs_data, noaa_data):
    """Predict flood probability using ML model or threshold"""
    
    flood_model, features = load_model()
    
    if flood_model == "threshold":
        # Simple threshold-based prediction as fallback
        if usgs_data:
            latest_usgs = sorted(usgs_data, key=lambda x: x['timestamp'])[-1]
            water_level = float(latest_usgs.get('water_level', 5.0))
            flood_stage = float(latest_usgs.get('flood_stage', 10.0))
            
            # Simple probability based on proximity to flood stage
            ratio = water_level / flood_stage
            if ratio > 0.9:
                return 0.8  # High probability
            elif ratio > 0.7:
                return 0.4  # Medium probability
            else:
                return 0.1  # Low probability
        else:
            return 0.1
    else:
        # Use ML model
        feature_vector = create_features(usgs_data, noaa_data)
        return flood_model.predict(feature_vector)[0]

def lambda_handler(event, context):
    """ML-powered flood prediction"""
    
    try:
        # Get recent data
        usgs_data, noaa_data = get_recent_data()
        
        # Make prediction
        flood_probability = predict_flood_probability(usgs_data, noaa_data)
        
        # Get account ID for SNS topics
        sts = boto3.client('sts')
        account_id = sts.get_caller_identity()['Account']
        
        # Determine alert level
        if flood_probability > 0.8:
            alert_level = "EMERGENCY"
            topic_arn = f"arn:aws:sns:us-east-1:{account_id}:flood-alerts-emergency"
            message = f"EMERGENCY: ML model predicts {flood_probability:.1%} flood probability in next 6 hours"
        elif flood_probability > 0.5:
            alert_level = "WARNING"
            topic_arn = f"arn:aws:sns:us-east-1:{account_id}:flood-alerts-warning"
            message = f"WARNING: ML model predicts {flood_probability:.1%} flood probability in next 6 hours"
        elif flood_probability > 0.2:
            alert_level = "WATCH"
            topic_arn = f"arn:aws:sns:us-east-1:{account_id}:flood-alerts-watch"
            message = f"WATCH: ML model predicts {flood_probability:.1%} flood probability in next 6 hours"
        else:
            alert_level = "NORMAL"
            topic_arn = None
            message = f"Normal conditions - {flood_probability:.1%} flood probability"
        
        # Send alert if needed
        if topic_arn and flood_probability > 0.2:
            sns = boto3.client('sns')
            sns.publish(
                TopicArn=topic_arn,
                Message=message,
                Subject=f'Potomac River Flood {alert_level}'
            )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'flood_probability': float(flood_probability),
                'alert_level': alert_level,
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Error in ML prediction: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }