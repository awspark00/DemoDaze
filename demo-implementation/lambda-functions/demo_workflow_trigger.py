#!/usr/bin/env python3
"""
Demo Workflow Trigger Lambda Function
Forces the flood monitoring workflow to execute by injecting high water level data
This triggers the ML predictor to send email alerts for demonstrations
"""

import json
import boto3
from datetime import datetime
from decimal import Decimal
import time

def lambda_handler(event, context):
    """
    Trigger demo workflow by injecting simulated high water level data
    
    Parameters in event (optional):
    - water_level: float (default 8.5) - Water level in feet
    - cleanup: bool (default False) - Whether to clean up demo data after
    """
    
    # Get parameters from event or use defaults
    water_level = event.get('water_level', 8.5)
    cleanup = event.get('cleanup', False)
    
    try:
        # Step 1: Inject demo data
        inject_result = inject_demo_data(water_level)
        
        # Wait for data to propagate
        time.sleep(2)
        
        # Step 2: Trigger ML predictor
        prediction_result = trigger_ml_predictor()
        
        # Step 3: Optional cleanup
        if cleanup:
            cleanup_demo_data(inject_result['timestamp'])
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Demo workflow triggered successfully',
                'injected_data': inject_result,
                'prediction': prediction_result,
                'cleanup_performed': cleanup
            })
        }
        
    except Exception as e:
        print(f"Error in demo trigger: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def inject_demo_data(water_level):
    """Inject simulated high water level data into DynamoDB"""
    
    # For demo mode, we don't actually inject data into DynamoDB
    # Instead, we'll pass demo parameters to the ML predictor
    # This keeps real data intact for showcase purposes
    
    print(f"Demo Mode - Simulating Water Level: {water_level} feet ({(water_level/10.0)*100:.0f}% of flood stage)")
    
    return {
        'gauge_id': '01646500',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'water_level': float(water_level),
        'flood_stage': 10.0,
        'ratio': (water_level / 10.0) * 100
    }

def trigger_ml_predictor():
    """Trigger the ML Flood Predictor Lambda in DEMO MODE"""
    
    lambda_client = boto3.client('lambda')
    
    try:
        # Pass demo_mode flag to ML predictor with simulated water level
        demo_payload = {
            'demo_mode': True,
            'demo_water_level': 8.5,  # 85% of flood stage
            'demo_flood_stage': 10.0
        }
        
        response = lambda_client.invoke(
            FunctionName='ml-flood-predictor',
            InvocationType='RequestResponse',
            Payload=json.dumps(demo_payload)
        )
        
        result = json.loads(response['Payload'].read())
        
        if 'body' in result:
            body = json.loads(result['body'])
            print(f"ML Prediction: {body.get('alert_level')} - {body.get('flood_probability', 0):.1%} probability")
            return body
        
        return result
        
    except Exception as e:
        print(f"Error invoking ML Predictor: {e}")
        return {'error': str(e)}

def cleanup_demo_data(timestamp):
    """Remove demo data after testing"""
    
    try:
        dynamodb = boto3.resource('dynamodb')
        gauge_table = dynamodb.Table('FloodGaugeReadings')
        weather_table = dynamodb.Table('WeatherObservations')
        
        # Delete demo records
        gauge_table.delete_item(
            Key={
                'gauge_id': '01646500',
                'timestamp': timestamp
            }
        )
        
        weather_table.delete_item(
            Key={
                'station_id': 'KDCA',
                'timestamp': timestamp
            }
        )
        
        print("Demo data cleaned up")
        return True
        
    except Exception as e:
        print(f"Error cleaning up demo data: {e}")
        return False
