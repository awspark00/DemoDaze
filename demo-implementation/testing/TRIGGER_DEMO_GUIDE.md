# Demo Workflow Trigger Guide

## Overview

This guide shows you how to trigger the complete flood monitoring workflow for demonstrations, forcing the system to send email alerts without modifying any Lambda code.

## How It Works

The demo trigger script:
1. **Injects simulated high water level data** into DynamoDB (8.5 feet - 85% of flood stage)
2. **Triggers the ML Flood Predictor Lambda** to analyze the data
3. **Sends a WARNING level email alert** to your subscribed email address
4. **Optionally cleans up** the demo data after testing

## Prerequisites

- AWS CLI configured with credentials
- Python 3.x with boto3 installed
- Email address subscribed to SNS topics (from CloudFormation deployment)
- Lambda functions deployed and operational

## Quick Start

### Option 1: Run the Python Script (Recommended)

```bash
cd demo-implementation/testing
python trigger-demo-workflow.py
```

The script will:
- Show you what it's about to do
- Wait for your confirmation
- Inject demo data
- Trigger the ML predictor
- Display results
- Optionally clean up

### Option 2: Manual AWS CLI Commands

If you prefer to trigger manually:

```bash
# 1. Inject demo data into DynamoDB
aws dynamodb put-item \
    --table-name FloodGaugeReadings \
    --item '{
        "gauge_id": {"S": "01646500"},
        "timestamp": {"S": "'$(date -u +%Y-%m-%dT%H:%M:%S.000Z)'"},
        "water_level": {"N": "8.5"},
        "flood_stage": {"N": "10.0"},
        "location_name": {"S": "POTOMAC RIVER NEAR WASH, DC"},
        "trend": {"S": "rising"},
        "ttl": {"N": "'$(($(date +%s) + 1209600))'"}
    }'

# 2. Trigger the ML Predictor Lambda
aws lambda invoke \
    --function-name MLFloodPredictor \
    --payload '{}' \
    response.json

# 3. View the results
cat response.json
```

## Expected Results

### Console Output

```
======================================================================
DEMO MODE: Injecting High Water Level Data
======================================================================

✓ Injected HIGH water level data:
  Gauge: Chain Bridge (01646500)
  Water Level: 8.5 feet
  Flood Stage: 10.0 feet
  Ratio: 85% (WARNING threshold)
  Timestamp: 2026-02-11T15:30:00.000Z

✓ Injected precipitation data:
  Station: KDCA
  Recent Precipitation: 0.5 inches
  Forecast: 2.0 inches in 24hr

======================================================================
TRIGGERING ML FLOOD PREDICTOR
======================================================================

✓ Lambda invoked successfully
  Status Code: 200

📊 Prediction Results:
  Flood Probability: 40.0%
  Alert Level: WARNING
  Message: WARNING: ML model predicts 40.0% flood probability in next 6 hours

✅ EMAIL ALERT SENT!
   Check your email for the flood alert notification
```

### Email Alert

You should receive an email with:
- **Subject**: `Potomac River Flood WARNING`
- **Message**: `WARNING: ML model predicts 40.0% flood probability in next 6 hours`
- **From**: AWS SNS (flood-alerts-warning topic)

## Alert Thresholds

The system uses these thresholds based on water level ratio to flood stage:

| Water Level | Ratio | Probability | Alert Level | Email Sent? |
|-------------|-------|-------------|-------------|-------------|
| < 7.0 feet  | < 70% | 10%         | NORMAL      | ❌ No       |
| 7.0-8.9 ft  | 70-89%| 40%         | WARNING     | ✅ Yes      |
| ≥ 9.0 feet  | ≥ 90% | 80%         | EMERGENCY   | ✅ Yes      |

## Demo Scenarios

### Scenario 1: WARNING Alert (Default)
```python
water_level = 8.5 feet  # 85% of flood stage
# Result: WARNING alert, 40% probability
```

### Scenario 2: EMERGENCY Alert
Modify the script to inject 9.5 feet:
```python
'water_level': Decimal('9.5'),  # 95% of flood stage
# Result: EMERGENCY alert, 80% probability
```

### Scenario 3: WATCH Alert
Modify the script to inject 7.5 feet:
```python
'water_level': Decimal('7.5'),  # 75% of flood stage
# Result: WARNING alert, 40% probability
```

## Troubleshooting

### No Email Received

1. **Check SNS subscription**: Verify your email is confirmed
   ```bash
   aws sns list-subscriptions
   ```

2. **Check spam folder**: SNS emails sometimes go to spam

3. **Verify Lambda execution**: Check CloudWatch Logs
   ```bash
   aws logs tail /aws/lambda/MLFloodPredictor --follow
   ```

4. **Check water level**: Must be ≥ 7.0 feet (70%) to trigger email

### Lambda Invocation Failed

1. **Verify Lambda exists**:
   ```bash
   aws lambda get-function --function-name MLFloodPredictor
   ```

2. **Check IAM permissions**: Ensure your AWS credentials can invoke Lambda

3. **View Lambda logs**:
   ```bash
   aws logs tail /aws/lambda/MLFloodPredictor --follow
   ```

### Data Not Found

The ML Predictor queries DynamoDB for recent data. If it doesn't find the injected data:
- Wait a few seconds and try again
- Check DynamoDB table exists: `FloodGaugeReadings`
- Verify timestamp format is correct

## Cleanup

### Automatic Cleanup
Demo data automatically expires after 14 days (TTL)

### Manual Cleanup
The script prompts you to clean up after demo, or run:
```bash
aws dynamodb delete-item \
    --table-name FloodGaugeReadings \
    --key '{"gauge_id": {"S": "01646500"}, "timestamp": {"S": "YOUR_TIMESTAMP"}}'
```

## Best Practices for Demos

1. **Test before live demo**: Run the script once to verify email delivery
2. **Check spam folder**: Ensure emails aren't filtered
3. **Time the demo**: Script takes ~5 seconds to complete
4. **Show the email**: Have your email open during demo to show real-time alert
5. **Explain the data**: Walk through the injected water levels and thresholds

## Integration with Presentations

This demo trigger is perfect for:
- **Live demonstrations** - Show real-time alerting
- **Customer presentations** - Prove the system works end-to-end
- **Testing** - Validate deployment before going live
- **Training** - Help operators understand the workflow

## Next Steps

After triggering the demo:
1. Show the email alert received
2. Check CloudWatch dashboard for metrics
3. Query DynamoDB to show stored data
4. Explain how the ML model made the prediction

---

**Note**: This demo uses simulated data. In production, the system monitors real USGS stream gauges and only sends alerts when actual flood conditions are detected.
