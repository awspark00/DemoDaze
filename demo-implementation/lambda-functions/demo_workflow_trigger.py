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

def lambda_handler(event, context):
    """
    Trigger demo workflow with simulated high water level data
    
    NOTE: This does NOT write to DynamoDB - it passes demo data directly to ML predictor
    This preserves real monitoring data for showcase purposes
    
    Parameters in event (optional):
    - water_level: float (default 8.5) - Water level in feet
    """
    
    # Get parameters from event or use defaults
    water_level = event.get('water_level', 8.5)
    
    try:
        # Step 1: Prepare demo data (logging only, no DynamoDB write)
        demo_info = prepare_demo_data(water_level)
        
        # Step 2: Trigger ML predictor with demo mode
        prediction_result = trigger_ml_predictor(water_level)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Demo workflow triggered successfully',
                'demo_info': demo_info,
                'prediction': prediction_result
            })
        }
        
    except Exception as e:
        print(f"Error in demo trigger: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def prepare_demo_data(water_level):
    """Prepare demo data parameters (does NOT write to DynamoDB)"""
    
    print(f"Demo Mode - Simulating Water Level: {water_level} feet ({(water_level/10.0)*100:.0f}% of flood stage)")
    
    return {
        'gauge_id': '01646500',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'water_level': float(water_level),
        'flood_stage': 10.0,
        'ratio': (water_level / 10.0) * 100
    }

def trigger_ml_predictor(water_level):
    """Trigger the ML Flood Predictor Lambda in DEMO MODE"""
    
    lambda_client = boto3.client('lambda')
    
    try:
        # Pass demo_mode flag to ML predictor with simulated water level
        demo_payload = {
            'demo_mode': True,
            'demo_water_level': water_level,
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
