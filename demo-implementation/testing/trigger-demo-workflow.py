#!/usr/bin/env python3
"""
Demo Workflow Trigger
Forces the flood monitoring workflow to execute by injecting high water level data
This triggers the ML predictor to send email alerts without modifying Lambda code
"""

import boto3
import json
from datetime import datetime, timedelta
from decimal import Decimal
import time

def inject_demo_data():
    """Inject simulated high water level data into DynamoDB"""
    
    dynamodb = boto3.resource('dynamodb')
    gauge_table = dynamodb.Table('FloodGaugeReadings')
    weather_table = dynamodb.Table('WeatherObservations')
    
    print("=" * 70)
    print("DEMO MODE: Injecting High Water Level Data")
    print("=" * 70)
    
    # Calculate TTL (2 days from now)
    ttl = int(time.time()) + (2 * 24 * 60 * 60)
    
    # Inject HIGH water level for Chain Bridge gauge (01646500)
    # Normal flood stage is 10.0 feet, we'll inject 8.5 feet (85% - triggers WARNING)
    current_time = datetime.utcnow().isoformat() + 'Z'
    
    demo_gauge_data = {
        'gauge_id': '01646500',
        'timestamp': current_time,
        'water_level': Decimal('8.5'),  # 85% of flood stage - triggers WARNING
        'flood_stage': Decimal('10.0'),
        'location_name': 'POTOMAC RIVER NEAR WASH, DC LITTLE FALLS PUMP STA',
        'trend': 'rising',
        'ttl': ttl
    }
    
    gauge_table.put_item(Item=demo_gauge_data)
    print(f"\n✓ Injected HIGH water level data:")
    print(f"  Gauge: Chain Bridge (01646500)")
    print(f"  Water Level: 8.5 feet")
    print(f"  Flood Stage: 10.0 feet")
    print(f"  Ratio: 85% (WARNING threshold)")
    print(f"  Timestamp: {current_time}")
    
    # Inject recent precipitation data
    demo_weather_data = {
        'station_id': 'KDCA',
        'timestamp': current_time,
        'precipitation_1hr': Decimal('0.5'),  # Half inch of rain
        'precipitation_forecast_24hr': Decimal('2.0'),  # 2 inches forecast
        'temperature': Decimal('15.0'),
        'location_name': 'Weather Station KDCA',
        'ttl': ttl
    }
    
    weather_table.put_item(Item=demo_weather_data)
    print(f"\n✓ Injected precipitation data:")
    print(f"  Station: KDCA")
    print(f"  Recent Precipitation: 0.5 inches")
    print(f"  Forecast: 2.0 inches in 24hr")
    
    return True

def trigger_ml_predictor():
    """Trigger the ML Flood Predictor Lambda"""
    
    lambda_client = boto3.client('lambda')
    
    print("\n" + "=" * 70)
    print("TRIGGERING ML FLOOD PREDICTOR")
    print("=" * 70)
    
    try:
        response = lambda_client.invoke(
            FunctionName='MLFloodPredictor',
            InvocationType='RequestResponse',
            Payload=json.dumps({})
        )
        
        result = json.loads(response['Payload'].read())
        
        print(f"\n✓ Lambda invoked successfully")
        print(f"  Status Code: {response['StatusCode']}")
        
        if 'body' in result:
            body = json.loads(result['body'])
            print(f"\n📊 Prediction Results:")
            print(f"  Flood Probability: {body.get('flood_probability', 0):.1%}")
            print(f"  Alert Level: {body.get('alert_level', 'UNKNOWN')}")
            print(f"  Message: {body.get('message', 'N/A')}")
            
            if body.get('flood_probability', 0) > 0.2:
                print(f"\n✅ EMAIL ALERT SENT!")
                print(f"   Check your email for the flood alert notification")
            else:
                print(f"\n⚠️  Probability too low - no email sent")
                print(f"   (Threshold is 20%, got {body.get('flood_probability', 0):.1%})")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error invoking Lambda: {e}")
        return None

def cleanup_demo_data():
    """Optional: Remove demo data after testing"""
    
    response = input("\n\nCleanup demo data? (y/n): ")
    
    if response.lower() == 'y':
        dynamodb = boto3.resource('dynamodb')
        gauge_table = dynamodb.Table('FloodGaugeReadings')
        
        # Delete the demo record
        gauge_table.delete_item(
            Key={
                'gauge_id': '01646500',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        )
        print("✓ Demo data cleaned up")
    else:
        print("Demo data left in place (will auto-expire in 14 days)")

def main():
    """Main demo workflow trigger"""
    
    print("\n" + "=" * 70)
    print("FLOOD MONITORING DEMO - WORKFLOW TRIGGER")
    print("=" * 70)
    print("\nThis script will:")
    print("1. Inject simulated HIGH water level data (85% of flood stage)")
    print("2. Trigger the ML Flood Predictor Lambda")
    print("3. Send a WARNING level email alert to your subscribed address")
    print("\n" + "=" * 70)
    
    input("\nPress Enter to start demo workflow...")
    
    # Step 1: Inject demo data
    inject_demo_data()
    
    # Wait a moment for data to be available
    print("\n⏳ Waiting 2 seconds for data to propagate...")
    time.sleep(2)
    
    # Step 2: Trigger ML predictor
    result = trigger_ml_predictor()
    
    # Step 3: Optional cleanup
    if result:
        cleanup_demo_data()
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
