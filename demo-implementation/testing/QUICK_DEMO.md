# Quick Demo - 3 Minutes

## Copy/Paste This Into DynamoDB

```json
{
  "gauge_id": "01646500",
  "timestamp": "2024-01-29T15:00:00Z",
  "water_level": 9.5,
  "flood_stage": 10.0,
  "location_name": "DEMO - POTOMAC RIVER AT CHAIN BRIDGE",
  "trend": "rising",
  "ttl": 1738252800
}
```

## Steps

1. **DynamoDB** → `FloodGaugeReadings` → Create item → JSON view → Paste above → Create
2. **Lambda** → `ml-flood-predictor` → Test tab → Test event: `{}` → Test
3. **Check email** → Should receive "EMERGENCY" alert

## Expected Result

```json
{
  "statusCode": 200,
  "body": {
    "flood_probability": 0.8,
    "alert_level": "EMERGENCY",
    "message": "EMERGENCY: ML model predicts 80.0% flood probability in next 6 hours"
  }
}
```

## Email Will Say

```
Subject: Potomac River Flood EMERGENCY

EMERGENCY: ML model predicts 80.0% flood probability in next 6 hours
```

---

## If Email Doesn't Arrive

1. Check spam folder
2. Verify SNS subscription confirmed
3. Check Lambda logs: Monitor → View CloudWatch logs
4. Look for: "Publishing to SNS topic"

---

## Cleanup After Demo

DynamoDB → `FloodGaugeReadings` → Find item with `water_level: 9.5` → Delete

---

## Alternative: Force Email Every Time

Modify Lambda temporarily:

```python
def predict_flood_probability(usgs_data, noaa_data):
    return 0.9  # DEMO MODE - REMOVE AFTER
```

Deploy → Test → Get email guaranteed
