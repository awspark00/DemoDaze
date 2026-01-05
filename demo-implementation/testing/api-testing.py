#!/usr/bin/env python3
"""
API Testing Script - Verify USGS and NOAA APIs Work
Run this to confirm data sources are available before building the demo
"""

import requests
import json
from datetime import datetime

def test_usgs_api():
    """Test USGS Water Services API"""
    print("🌊 Testing USGS Water Services API...")
    
    # Potomac River gauges
    usgs_url = "https://waterservices.usgs.gov/nwis/iv/"
    params = {
        'format': 'json',
        'sites': '01646500,01594440,01638500',  # 3 Potomac River gauges
        'parameterCd': '00065',  # Gauge height
        'period': 'PT4H'  # Last 4 hours
    }
    
    try:
        response = requests.get(usgs_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"✅ USGS API Response: {response.status_code}")
        print(f"📊 Number of gauge sites: {len(data['value']['timeSeries'])}")
        
        for site in data['value']['timeSeries']:
            gauge_id = site['sourceInfo']['siteCode'][0]['value']
            location = site['sourceInfo']['siteName']
            readings = len(site['values'][0]['value'])
            
            if readings > 0:
                latest_reading = site['values'][0]['value'][0]
                water_level = latest_reading['value']
                timestamp = latest_reading['dateTime']
                
                print(f"   📍 {gauge_id}: {location}")
                print(f"      Latest: {water_level} ft at {timestamp}")
                print(f"      Readings available: {readings}")
            
        return True
        
    except Exception as e:
        print(f"❌ USGS API Error: {e}")
        return False

def test_noaa_weather_api():
    """Test NOAA Weather API"""
    print("\n🌤️ Testing NOAA Weather API...")
    
    # DC area weather stations
    stations = ['KDCA', 'KIAD', 'KADW']
    
    success_count = 0
    
    for station in stations:
        try:
            obs_url = f"https://api.weather.gov/stations/{station}/observations/latest"
            response = requests.get(obs_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            properties = data['properties']
            
            timestamp = properties.get('timestamp', 'N/A')
            temp = properties.get('temperature', {}).get('value')
            precip = properties.get('precipitationLastHour', {}).get('value')
            
            print(f"✅ {station}: {response.status_code}")
            print(f"   🌡️ Temperature: {temp}°C")
            print(f"   🌧️ Precipitation (1hr): {precip} mm")
            print(f"   ⏰ Timestamp: {timestamp}")
            
            success_count += 1
            
        except Exception as e:
            print(f"❌ {station} Error: {e}")
    
    return success_count > 0

def test_noaa_alerts_api():
    """Test NOAA Alerts API"""
    print("\n🚨 Testing NOAA Alerts API...")
    
    try:
        alerts_url = "https://api.weather.gov/alerts"
        params = {
            'area': 'DC',
            'status': 'actual',
            'message_type': 'alert'
        }
        
        response = requests.get(alerts_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        alerts = data.get('features', [])
        
        print(f"✅ NOAA Alerts API Response: {response.status_code}")
        print(f"🚨 Active alerts for DC area: {len(alerts)}")
        
        if alerts:
            for alert in alerts[:3]:  # Show first 3 alerts
                properties = alert['properties']
                event = properties.get('event', 'Unknown')
                headline = properties.get('headline', 'No headline')
                severity = properties.get('severity', 'Unknown')
                
                print(f"   ⚠️ {event} ({severity})")
                print(f"      {headline}")
        else:
            print("   ✅ No active alerts (good news!)")
            
        return True
        
    except Exception as e:
        print(f"❌ NOAA Alerts API Error: {e}")
        return False

def test_noaa_forecast_api():
    """Test NOAA Forecast API for DC area"""
    print("\n🔮 Testing NOAA Forecast API...")
    
    try:
        # Get forecast for Washington DC area
        forecast_url = "https://api.weather.gov/gridpoints/LWX/97,71/forecast"
        response = requests.get(forecast_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        periods = data['properties']['periods']
        
        print(f"✅ NOAA Forecast API Response: {response.status_code}")
        print(f"📅 Forecast periods available: {len(periods)}")
        
        # Show next 3 periods
        for period in periods[:3]:
            name = period.get('name', 'Unknown')
            temp = period.get('temperature', 'N/A')
            forecast = period.get('shortForecast', 'No forecast')
            
            print(f"   📊 {name}: {temp}°F - {forecast}")
            
        return True
        
    except Exception as e:
        print(f"❌ NOAA Forecast API Error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🧪 Testing Public APIs for Flood Monitoring Demo")
    print("=" * 60)
    
    results = {
        'usgs': test_usgs_api(),
        'noaa_weather': test_noaa_weather_api(),
        'noaa_alerts': test_noaa_alerts_api(),
        'noaa_forecast': test_noaa_forecast_api()
    }
    
    print("\n" + "=" * 60)
    print("📋 API Test Results Summary:")
    
    for api, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {api.upper()}: {status}")
    
    all_pass = all(results.values())
    
    if all_pass:
        print("\n🎉 ALL APIS WORKING! Demo is feasible to build.")
        print("💡 Next step: Start implementing Phase 1 (AWS Lambda functions)")
    else:
        print("\n⚠️ Some APIs failed. Check network connection and try again.")
        print("💡 Demo may still be possible with working APIs only.")
    
    return all_pass

if __name__ == "__main__":
    main()