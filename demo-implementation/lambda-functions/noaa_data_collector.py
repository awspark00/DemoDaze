#!/usr/bin/env python3
"""
NOAA Data Collector Lambda Function
Collects weather data from NOAA Weather API
"""

import json
import boto3
import requests
from datetime import datetime
from decimal import Decimal

def lambda_handler(event, context):
    """Collect NOAA weather data for DC metro area"""
    
    # DC area weather stations
    stations = ['KDCA', 'KIAD', 'KADW']
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('WeatherObservations')
    
    records_processed = 0
    errors = []
    
    for station in stations:
        try:
            # Get current observations
            obs_url = f"https://api.weather.gov/stations/{station}/observations/latest"
            response = requests.get(obs_url, timeout=30, headers={'User-Agent': 'FloodMonitoringSystem/1.0'})
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if 'properties' not in data:
                    error_msg = f"Station {station}: Unexpected API response structure"
                    print(error_msg)
                    errors.append(error_msg)
                    continue
                
                properties = data['properties']
                
                # Extract precipitation data
                precip_1hr = properties.get('precipitationLastHour', {})
                precip_value = precip_1hr.get('value') if precip_1hr else None
                
                # Convert mm to inches (USGS uses feet, easier to work in inches)
                precip_inches = 0.0
                if precip_value:
                    precip_inches = float(precip_value) * 0.0393701  # mm to inches
                
                # Get forecast data (simplified - would need gridpoint lookup)
                forecast_precip_24hr = 0.0  # Would fetch from forecast API
                
                # Calculate TTL (14 days from now - optimized for fast collection)
                import time
                ttl = int(time.time()) + (14 * 24 * 60 * 60)  # 14 days in seconds
                
                # Store observation
                table.put_item(Item={
                    'station_id': station,
                    'timestamp': properties['timestamp'],
                    'precipitation_1hr': Decimal(str(precip_inches)),
                    'precipitation_forecast_24hr': Decimal(str(forecast_precip_24hr)),
                    'temperature': Decimal(str(properties.get('temperature', {}).get('value', 0) or 0)),
                    'location_name': f"Weather Station {station}",
                    'ttl': ttl
                })
                
                records_processed += 1
            else:
                error_msg = f"Station {station}: HTTP {response.status_code}"
                print(error_msg)
                errors.append(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = f"Station {station}: Request timeout"
            print(error_msg)
            errors.append(error_msg)
            continue
        except requests.exceptions.RequestException as req_err:
            error_msg = f"Station {station}: Request failed - {str(req_err)}"
            print(error_msg)
            errors.append(error_msg)
            continue
        except Exception as e:
            error_msg = f"Station {station}: Processing error - {str(e)}"
            print(error_msg)
            errors.append(error_msg)
            continue
    
    # Also check for active flood warnings
    try:
        alerts_url = "https://api.weather.gov/alerts"
        params = {'area': 'DC', 'event': 'Flood'}
        response = requests.get(alerts_url, params=params, timeout=30)
        
        if response.status_code == 200:
            alerts_data = response.json()
            active_warnings = len(alerts_data.get('features', []))
            
            # Calculate TTL (14 days from now - optimized for fast collection)
            import time
            ttl = int(time.time()) + (14 * 24 * 60 * 60)  # 14 days in seconds
            
            # Store alert status
            table.put_item(Item={
                'station_id': 'ALERTS_DC',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'active_flood_warnings': active_warnings,
                'location_name': 'DC Area Flood Alerts',
                'ttl': ttl
            })
            
    except Exception as e:
        print(f"Error checking flood alerts: {str(e)}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'NOAA data processed successfully',
            'records_processed': records_processed,
            'errors': errors if errors else None
        })
    }