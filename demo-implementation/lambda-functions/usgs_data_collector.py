#!/usr/bin/env python3
"""
USGS Data Collector Lambda Function
Collects stream gauge data from USGS Water Services API
"""

import json
import boto3
import requests
from datetime import datetime
from decimal import Decimal

def lambda_handler(event, context):
    """Collect USGS stream gauge data for Potomac River basin"""
    
    # Potomac River gauges
    usgs_url = "https://waterservices.usgs.gov/nwis/iv/"
    params = {
        'format': 'json',
        'sites': '01646500,01594440,01638500',  # 3 Potomac gauges
        'parameterCd': '00065',  # Gauge height
        'period': 'PT4H'  # Last 4 hours
    }
    
    try:
        response = requests.get(usgs_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Store in DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('FloodGaugeReadings')
        
        records_processed = 0
        
        for site in data['value']['timeSeries']:
            gauge_id = site['sourceInfo']['siteCode'][0]['value']
            location_name = site['sourceInfo']['siteName']
            
            # Set flood stages for each gauge
            flood_stages = {
                '01646500': 10.0,  # Chain Bridge
                '01594440': 15.0,  # Patuxent River
                '01638500': 18.0   # Point of Rocks
            }
            flood_stage = flood_stages.get(gauge_id, 10.0)
            
            for reading in site['values'][0]['value']:
                if reading['value'] and reading['value'] != '-999999':
                    water_level = Decimal(str(reading['value']))
                    
                    # Calculate trend (simplified)
                    trend = 'stable'  # Would calculate from previous readings
                    
                    # Calculate TTL (14 days from now - optimized for fast collection)
                    import time
                    ttl = int(time.time()) + (14 * 24 * 60 * 60)  # 14 days in seconds
                    
                    # Store reading
                    table.put_item(Item={
                        'gauge_id': gauge_id,
                        'timestamp': reading['dateTime'],
                        'water_level': water_level,
                        'flood_stage': Decimal(str(flood_stage)),
                        'location_name': location_name,
                        'trend': trend,
                        'ttl': ttl
                    })
                    
                    records_processed += 1
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'USGS data processed successfully',
                'records_processed': records_processed
            })
        }
        
    except Exception as e:
        print(f"Error processing USGS data: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }