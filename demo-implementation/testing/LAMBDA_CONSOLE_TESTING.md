# Testing Lambda Functions in AWS Console

## Quick Answer

Yes, you can test your Lambdas directly in the AWS Console! Here's how:

---

## Test Event for All 3 Lambdas

Your Lambda functions don't need any input, so use this simple test event:

```json
{}
```

That's it! Just an empty object.

---

## Step-by-Step: Testing in Lambda Console

### 1. Test USGS Data Collector

1. Go to AWS Console → Lambda → Functions
2. Click on `usgs-data-collector`
3. Click the **"Test"** tab
4. Click **"Create new event"**
5. Event name: `test-usgs`
6. Event JSON: `{}`
7. Click **"Save"**
8. Click **"Test"** button

**Expected Result**:
```json
{
  "statusCode": 200,
  "body": "{\"message\": \"USGS data processed successfully\", \"records_processed\": 6}"
}
```

**What to check**:
- Status code is 200 ✅
- Records processed > 0 ✅
- No errors in logs ✅

---

### 2. Test NOAA Data Collector

1. Go to Lambda → `noaa-data-collector`
2. Click **"Test"** tab
3. Create new event: `test-noaa`
4. Event JSON: `{}`
5. Click **"Test"**

**Expected Result**:
```json
{
  "statusCode": 200,
  "body": "{\"message\": \"NOAA data processed successfully\", \"records_processed\": 3}"
}
```

**What to check**:
- Status code is 200 ✅
- Records processed = 3 (3 weather stations) ✅
- No errors in logs ✅

---

### 3. Test ML Flood Predictor (The Important One!)

1. Go to Lambda → `ml-flood-predictor`
2. Click **"Test"** tab
3. Create new event: `test-ml`
4. Event JSON: `{}`
5. Click **"Test"**

**Expected Result** (with current low water levels):
```json
{
  "statusCode": 200,
  "body": "{\"flood_probability\": 0.1, \"alert_level\": \"NORMAL\", \"message\": \"Normal conditions - 10.0% flood probability\", \"timestamp\": \"2024-01-15T10:00:00.000000\"}"
}
```

**What to check**:
- Status code is 200 ✅
- Alert level is "NORMAL" ✅
- Flood probability is low (0.1 = 10%) ✅
- **No email sent** (because probability < 20%) ✅

---

## Understanding the Results

### If You See This (Current Reality):
```json
{
  "alert_level": "NORMAL",
  "flood_probability": 0.1
}
```
**Meaning**: Water levels are low, no alert sent. **System working correctly!**

### If You See This (Would trigger email):
```json
{
  "alert_level": "WARNING",
  "flood_probability": 0.4
}
```
**Meaning**: Water levels are high (7+ feet), email would be sent via SNS.

### If You See This (Emergency):
```json
{
  "alert_level": "EMERGENCY",
  "flood_probability": 0.8
}
```
**Meaning**: Water levels critical (9+ feet), emergency email sent.

---

## Checking CloudWatch Logs

After testing, check the logs:

1. In Lambda console, click **"Monitor"** tab
2. Click **"View CloudWatch logs"**
3. Click the latest log stream
4. Look for:
   - `"USGS data processed successfully"` ✅
   - `"records_processed": 6` ✅
   - Any error messages ❌

---

## Verifying Data Was Stored

### Check DynamoDB:

1. Go to AWS Console → DynamoDB → Tables
2. Click `FloodGaugeReadings`
3. Click **"Explore table items"**
4. You should see recent records with:
   - `gauge_id`: "01646500"
   - `water_level`: ~5.0 (current level)
   - `flood_stage`: 10.0
   - `timestamp`: Recent timestamp

Do the same for `WeatherObservations` table.

---

## Force a Test Alert (Advanced)

If you want to test email delivery, you need to inject high water data first.

### Option 1: Modify Lambda Temporarily

In `ml_flood_predictor.py`, add this at the start of `predict_flood_probability()`:

```python
def predict_flood_probability(usgs_data, noaa_data):
    # TEMPORARY TEST - REMOVE AFTER TESTING
    return 0.9  # Force EMERGENCY alert
    
    # ... rest of function
```

Redeploy Lambda, test it, and you'll get an email immediately.

**Remember to remove this after testing!**

### Option 2: Inject Test Data via DynamoDB

1. Go to DynamoDB → `FloodGaugeReadings`
2. Click **"Create item"**
3. Add:
```json
{
  "gauge_id": "01646500",
  "timestamp": "2024-01-15T10:00:00Z",
  "water_level": 9.5,
  "flood_stage": 10.0,
  "location_name": "TEST - Chain Bridge",
  "ttl": 1737000000
}
```
4. Save
5. Test `ml-flood-predictor` Lambda
6. Check your email!

---

## Troubleshooting

### "Function returned error"
- Check CloudWatch logs for details
- Verify IAM role has DynamoDB and SNS permissions
- Check if DynamoDB tables exist

### "No records processed"
- APIs might be down (rare)
- Check CloudWatch logs for API errors
- Run `api-testing.py` locally to verify APIs work

### "Test passed but no email"
- **This is expected!** Water levels are too low
- Probability must be > 20% to send email
- Current levels give ~10% probability
- Use "Force a Test Alert" methods above

---

## Quick Test Commands (AWS CLI)

If you prefer command line:

```bash
# Test USGS collector
aws lambda invoke --function-name usgs-data-collector response.json
type response.json

# Test NOAA collector
aws lambda invoke --function-name noaa-data-collector response.json
type response.json

# Test ML predictor
aws lambda invoke --function-name ml-flood-predictor response.json
type response.json
```

---

## Summary

| Lambda | Test Event | Expected Result | Email Sent? |
|--------|------------|-----------------|-------------|
| usgs-data-collector | `{}` | 200, records_processed: 6 | No |
| noaa-data-collector | `{}` | 200, records_processed: 3 | No |
| ml-flood-predictor | `{}` | 200, alert_level: NORMAL | No (water too low) |

**All 3 should return status 200 with no errors.**

**No email is sent because current water levels are below alert threshold (working correctly!).**
