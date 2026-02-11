# Lambda Functions Summary

You have **3 Lambda functions** that work together to monitor floods and send email alerts.

---

## 1️⃣ usgs_data_collector.py

**Purpose**: Collect river water level data

**Runs**: Every 15 minutes (EventBridge trigger)

**What it does**:
```
1. Call USGS API: https://waterservices.usgs.gov/nwis/iv/
2. Get water levels from 3 Potomac River gauges:
   - 01646500 (Chain Bridge) - Flood stage: 10 feet
   - 01594440 (Patuxent River) - Flood stage: 15 feet
   - 01638500 (Point of Rocks) - Flood stage: 18 feet
3. Store readings in DynamoDB table: FloodGaugeReadings
```

**Example data stored**:
```json
{
  "gauge_id": "01646500",
  "timestamp": "2024-01-15T10:00:00Z",
  "water_level": 5.2,
  "flood_stage": 10.0,
  "location_name": "POTOMAC RIVER AT CHAIN BRIDGE"
}
```

**Key code snippet**:
```python
# Fetch from USGS
response = requests.get(usgs_url, params={
    'sites': '01646500,01594440,01638500',
    'parameterCd': '00065'  # Gauge height
})

# Store in DynamoDB
table.put_item(Item={
    'gauge_id': gauge_id,
    'water_level': water_level,
    'flood_stage': flood_stage
})
```

---

## 2️⃣ noaa_data_collector.py

**Purpose**: Collect weather data (precipitation)

**Runs**: Every 20 minutes (EventBridge trigger)

**What it does**:
```
1. Call NOAA API: https://api.weather.gov/stations/{station}/observations/latest
2. Get weather from 3 DC area stations:
   - KDCA (Reagan National Airport)
   - KIAD (Dulles Airport)
   - KADW (Andrews Air Force Base)
3. Store observations in DynamoDB table: WeatherObservations
4. Also check for active flood warnings
```

**Example data stored**:
```json
{
  "station_id": "KDCA",
  "timestamp": "2024-01-15T10:00:00Z",
  "precipitation_1hr": 0.02,
  "temperature": 15.0,
  "location_name": "Weather Station KDCA"
}
```

**Key code snippet**:
```python
# Fetch from NOAA
response = requests.get(f"https://api.weather.gov/stations/{station}/observations/latest")

# Convert mm to inches
precip_inches = precip_value * 0.0393701

# Store in DynamoDB
table.put_item(Item={
    'station_id': station,
    'precipitation_1hr': precip_inches,
    'temperature': temperature
})
```

---

## 3️⃣ ml_flood_predictor.py ⭐ (This is the important one!)

**Purpose**: Predict flood probability and send email alerts

**Runs**: Every 2 hours (EventBridge trigger)

**What it does**:
```
1. Read recent water levels from DynamoDB (FloodGaugeReadings)
2. Read recent weather data from DynamoDB (WeatherObservations)
3. Calculate flood probability using threshold model:
   - If water level > 90% of flood stage → 80% probability (EMERGENCY)
   - If water level > 70% of flood stage → 40% probability (WARNING)
   - Otherwise → 10% probability (NORMAL)
4. Determine alert level based on probability:
   - > 80% → EMERGENCY
   - > 50% → WARNING
   - > 20% → WATCH
   - < 20% → NORMAL (no alert)
5. Send email via SNS if probability > 20%
```

**The Critical Logic** (why you're not getting emails):
```python
# Calculate ratio of current water to flood stage
ratio = water_level / flood_stage

# Determine probability
if ratio > 0.9:    # 90% of flood stage (9+ feet)
    probability = 0.8  # 80% → EMERGENCY alert
elif ratio > 0.7:  # 70% of flood stage (7+ feet)
    probability = 0.4  # 40% → WARNING alert
else:
    probability = 0.1  # 10% → NO ALERT

# Send email ONLY if probability > 20%
if probability > 0.2:
    sns.publish(
        TopicArn=topic_arn,
        Message=f"Flood probability: {probability}",
        Subject=f"Potomac River Flood {alert_level}"
    )
```

**Why you're not getting emails**:
- Current water level: ~5 feet
- Flood stage: 10 feet
- Ratio: 5/10 = 0.5 (50%)
- Probability: 0.1 (10%)
- **10% < 20% threshold → NO EMAIL SENT** ✅ Correct behavior!

---

## How They Work Together

```
┌─────────────────────────────────────────────────────────────┐
│                    EVERY 15 MINUTES                         │
│  usgs_data_collector.py → DynamoDB (FloodGaugeReadings)    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    EVERY 20 MINUTES                         │
│  noaa_data_collector.py → DynamoDB (WeatherObservations)   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    EVERY 2 HOURS                            │
│  ml_flood_predictor.py:                                     │
│    1. Read DynamoDB data                                    │
│    2. Calculate flood probability                           │
│    3. If probability > 20% → Send email via SNS             │
└─────────────────────────────────────────────────────────────┘
                              ↓
                         📧 EMAIL
```

---

## Quick Reference

| Lambda | Trigger | What It Does | Output |
|--------|---------|--------------|--------|
| usgs_data_collector | Every 15 min | Get river levels | DynamoDB |
| noaa_data_collector | Every 20 min | Get weather data | DynamoDB |
| ml_flood_predictor | Every 2 hours | Calculate risk & send email | SNS → Email |

---

## File Locations

All Lambda functions are in: `Demo Daze/demo-implementation/lambda-functions/`

- `usgs_data_collector.py` (67 lines)
- `noaa_data_collector.py` (78 lines)
- `ml_flood_predictor.py` (156 lines)

---

## To View Them

Open any of these files in your editor to see the actual code.

The most important one is **ml_flood_predictor.py** - that's the one that decides whether to send emails.
