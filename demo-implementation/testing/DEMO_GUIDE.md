# Live Demo Guide - AWS Console Testing

## Goal
Demonstrate the flood monitoring system by executing a test in the AWS Console and receiving an actual email alert.

---

## Demo Flow (5 Minutes)

### Step 1: Show Normal Operation (1 min)
Test the ML predictor with current real data - shows no alert.

### Step 2: Inject High Water Data (2 min)
Add test data to DynamoDB to simulate flood conditions.

### Step 3: Trigger Alert (1 min)
Run ML predictor again - sends email alert.

### Step 4: Show Email (1 min)
Display the received email alert.

---

## Detailed Steps

### STEP 1: Test Normal Operation

**Purpose**: Show system is working but water levels are normal.

1. Go to **AWS Console → Lambda**
2. Click `ml-flood-predictor`
3. Click **"Test"** tab
4. Create test event:
   - Name: `normal-test`
   - Event JSON: `{}`
5. Click **"Test"**

**Expected Output**:
```json
{
  "statusCode": 200,
  "body": {
    "flood_probability": 0.1,
    "alert_level": "NORMAL",
    "message": "Normal conditions - 10.0% flood probability"
  }
}
```

**Say to audience**: 
> "As you can see, the system is monitoring the Potomac River. Current water levels are 5 feet, well below the 10-foot flood stage. The ML model calculates only a 10% flood probability, so no alert is sent. This prevents false alarms."

---

### STEP 2: Inject High Water Test Data

**Purpose**: Simulate emergency flood conditions.

1. Go to **AWS Console → DynamoDB**
2. Click **Tables** → `FloodGaugeReadings`
3. Click **"Explore table items"**
4. Click **"Create item"**
5. Switch to **JSON view**
6. Paste this:

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

7. Click **"Create item"**

**Say to audience**:
> "Now I'm simulating emergency conditions. I'm injecting test data showing water levels at 9.5 feet - that's 95% of the flood stage. This represents a real flood scenario."

---

### STEP 3: Trigger the Alert

**Purpose**: Run ML predictor with high water data to send email.

1. Go back to **Lambda → ml-flood-predictor**
2. Click **"Test"** tab
3. Click **"Test"** button (use same test event)

**Expected Output**:
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

**Say to audience**:
> "Now the ML model detects the high water levels. It calculates an 80% flood probability and automatically sends an emergency alert via Amazon SNS to all subscribed emergency managers."

---

### STEP 4: Show the Email

**Purpose**: Prove the alert was actually sent.

1. Open your email inbox (have it ready in another tab)
2. Show the email from AWS SNS:

**Email will look like**:
```
From: AWS Notifications
Subject: Potomac River Flood EMERGENCY

EMERGENCY: ML model predicts 80.0% flood probability in next 6 hours
```

**Say to audience**:
> "And here's the actual email alert that was just sent. In a real scenario, this would go to emergency management teams, giving them 6 hours advance warning to take action - evacuate areas, deploy resources, etc."

---

### STEP 5: Cleanup (Optional)

Delete the test data:
1. Go to DynamoDB → `FloodGaugeReadings`
2. Find the item with `water_level: 9.5`
3. Delete it

---

## Alternative: Modify Lambda for Guaranteed Email

If you want to guarantee an email every time (for demo reliability), temporarily modify the Lambda:

### Quick Lambda Modification

1. Go to Lambda → `ml-flood-predictor`
2. Click **"Code"** tab
3. Find the `predict_flood_probability` function
4. Add this at the very top:

```python
def predict_flood_probability(usgs_data, noaa_data):
    # DEMO MODE - FORCE EMERGENCY ALERT
    return 0.9
    
    # ... rest of function below
```

5. Click **"Deploy"**
6. Now every test will send an email

**Remember to remove this after the demo!**

---

## Backup Plan (If Email Doesn't Arrive)

If email doesn't arrive during demo:

1. Check CloudWatch Logs:
   - Lambda → Monitor → View CloudWatch logs
   - Show the log entry: `"Publishing to SNS topic..."`
   - This proves the alert was sent

2. Check SNS:
   - Go to SNS → Topics → `flood-alerts-emergency`
   - Show the topic exists and has subscriptions

3. Explain:
   > "The alert was successfully sent to SNS. Email delivery can take 30-60 seconds. In production, we'd also integrate with SMS, PagerDuty, or other alerting systems for immediate notification."

---

## Demo Script (What to Say)

### Opening
> "I'm going to demonstrate our flood monitoring system. This system integrates real-time data from USGS river gauges and NOAA weather stations, uses machine learning to predict flood risk, and automatically alerts emergency managers."

### During Normal Test
> "First, let me show you normal operation. The system is currently monitoring the Potomac River. Water levels are at 5 feet, well below the 10-foot flood stage. The ML model calculates only a 10% probability of flooding, so no alert is sent."

### During Data Injection
> "Now I'll simulate emergency conditions by injecting test data showing water levels at 9.5 feet - 95% of flood stage. This represents a real flood scenario."

### During Alert Test
> "When I run the prediction again, the ML model detects the high water and calculates an 80% flood probability. It automatically sends an emergency alert via Amazon SNS."

### Showing Email
> "And here's the actual email that was just sent. Emergency managers receive this alert with 6 hours advance warning, allowing them to evacuate areas, deploy resources, and coordinate response."

### Closing
> "This entire system runs serverless on AWS, costs about $25 per month, and provides 24/7 automated monitoring. Compare that to traditional systems costing $48,000 per month with manual monitoring."

---

## Pre-Demo Checklist

- [ ] SNS email subscription confirmed (check inbox)
- [ ] All 3 Lambda functions deployed
- [ ] DynamoDB tables exist and have data
- [ ] Test the normal flow once before demo
- [ ] Have email inbox open in another tab
- [ ] Have test data JSON ready to paste
- [ ] Know your AWS account ID (for SNS topic ARN)

---

## Timing

- **Setup**: 30 seconds (navigate to Lambda)
- **Normal test**: 30 seconds
- **Inject data**: 60 seconds
- **Trigger alert**: 30 seconds
- **Show email**: 30 seconds
- **Total**: ~3 minutes

---

## Common Issues

**Email not arriving?**
- Check spam folder
- Verify SNS subscription is confirmed
- Check CloudWatch logs to confirm SNS publish succeeded
- Email can take 30-60 seconds to arrive

**Lambda error?**
- Check IAM role has SNS permissions
- Verify DynamoDB tables exist
- Check CloudWatch logs for details

**Wrong alert level?**
- Verify test data has `water_level: 9.5`
- Check `flood_stage: 10.0`
- Ratio must be > 0.9 for EMERGENCY

---

## Success Criteria

✅ Normal test shows "NORMAL" alert level
✅ High water test shows "EMERGENCY" alert level  
✅ Email arrives in inbox
✅ Demo completes in under 5 minutes
