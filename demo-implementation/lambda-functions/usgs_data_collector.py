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
        
        # Validate response structure
        if 'value' not in data or 'timeSeries' not in data['value']:
            print("Warning: Unexpected USGS API response structure")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'USGS API returned unexpected format - no data processed',
                    'records_processed': 0
                })
            }
        
        # Store in DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('FloodGaugeReadings')
        
        records_processed = 0
        errors = []
        
        for site in data['value']['timeSeries']:
            try:
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
                        
                        # Calculate TTL (2 days from now)
                        import time
                        ttl = int(time.time()) + (2 * 24 * 60 * 60)  # 2 days in seconds
                        
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
            except Exception as site_error:
                error_msg = f"Error processing gauge {gauge_id}: {str(site_error)}"
                print(error_msg)
                errors.append(error_msg)
                continue  # Continue processing other gauges
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'USGS data processed successfully',
                'records_processed': records_processed,
                'errors': errors if errors else None
            })
        }
        
    except requests.exceptions.Timeout:
        print("Error: USGS API request timed out after 30 seconds")
        return {
            'statusCode': 504,
            'body': json.dumps({
                'error': 'USGS API timeout',
                'message': 'Request timed out - will retry on next scheduled run'
            })
        }
    except requests.exceptions.HTTPError as http_err:
        print(f"Error: USGS API HTTP error: {http_err}")
        return {
            'statusCode': response.status_code if 'response' in locals() else 500,
            'body': json.dumps({
                'error': 'USGS API HTTP error',
                'message': str(http_err),
                'note': 'Will retry on next scheduled run'
            })
        }
    except requests.exceptions.RequestException as req_err:
        print(f"Error: USGS API request failed: {req_err}")
        return {
            'statusCode': 503,
            'body': json.dumps({
                'error': 'USGS API unavailable',
                'message': str(req_err),
                'note': 'Will retry on next scheduled run'
            })
        }
    except Exception as e:
        print(f"Error processing USGS data: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal processing error',
                'message': str(e)
            })
        }