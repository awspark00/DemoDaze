# Federal Flood Monitoring System - Demo Script
## Real-Time Inter-Agency Data Integration with AI/ML Predictions

---

## Demo Overview (30 seconds)
**"Today I'm demonstrating a federal flood monitoring system that integrates real-time data from USGS and NOAA to provide AI-powered flood predictions with 6-hour advance warning. This system has been running continuously for over 2 weeks, collecting data every 15-20 minutes and generating ML predictions every 2 hours."**

---

## Part 1: Architecture Overview (2 minutes)

### Show: Architecture Diagram
**"Let me start with the system architecture. This demonstrates modern inter-agency collaboration between USGS and NOAA through AWS cloud services."**

**Key Points to Highlight:**
- **Data Sources**: USGS stream gauges + NOAA weather stations
- **Serverless Architecture**: Lambda functions, DynamoDB, EventBridge automation
- **ML Pipeline**: SageMaker training → S3 model storage → Lambda predictions
- **Alerting**: SNS topics for graduated flood warnings
- **Cost**: $25/month vs $48,000 traditional systems (99% reduction)

---

## Part 2: Live Data Collection - USGS Lambda (3 minutes)

### Show: AWS Lambda Console → usgs-data-collector
**"First, let's look at our USGS data collection. This Lambda function runs every 15 minutes to collect stream gauge data from the Potomac River basin."**

#### Demo Steps:
1. **Open Lambda Function**: Show `usgs-data-collector` function
2. **Show Code**: Highlight key sections:
   - API endpoint: `https://waterservices.usgs.gov/nwis/iv/`
   - Three Potomac gauges: `01646500,01594440,01638500`
   - Real-time water level collection
3. **Show Recent Executions**: CloudWatch logs showing successful runs
4. **Test Function**: Click "Test" to run live data collection
5. **Show Output**: Display successful API response and records processed

**Talking Points:**
- "This connects to live USGS APIs - no mock data"
- "Collecting from 3 strategic Potomac River monitoring points"
- "Each run processes ~99 water level readings"

---

## Part 3: Live Data Collection - NOAA Lambda (2 minutes)

### Show: AWS Lambda Console → noaa-data-collector
**"Next is our NOAA weather data collection, running every 20 minutes to gather precipitation and temperature data from DC area weather stations."**

#### Demo Steps:
1. **Open Lambda Function**: Show `noaa-data-collector` function
2. **Show Code**: Highlight:
   - Weather stations: `KDCA, KIAD, KADW`
   - Precipitation data conversion (mm to inches)
   - Temperature readings
3. **Test Function**: Run live collection
4. **Show Output**: Weather data successfully collected

**Talking Points:**
- "Real NOAA weather API integration"
- "DC metro area coverage for comprehensive weather context"
- "Precipitation is key input for flood prediction models"

---

## Part 4: Data Storage - DynamoDB Tables (3 minutes)

### Show: DynamoDB Console
**"All this real-time data flows into DynamoDB tables optimized for time-series analysis and cost control."**

#### Demo Steps:
1. **FloodGaugeReadings Table**:
   - Show table structure (gauge_id, timestamp, water_level, flood_stage)
   - **Scan/Query**: Display recent USGS readings
   - **Highlight TTL**: Point out 14-day auto-expiration for cost optimization
   - **Show Volume**: "~9,500 readings per day from continuous collection"

2. **WeatherObservations Table**:
   - Show table structure (station_id, timestamp, precipitation, temperature)
   - **Display Recent Data**: NOAA weather readings
   - **Show Integration**: How weather correlates with water levels

**Talking Points:**
- "2+ weeks of continuous data collection"
- "14-day TTL maintains ~2,352 records for ML training"
- "Cost-optimized: Pay only for what we use"

---

## Part 5: Machine Learning Pipeline - SageMaker (4 minutes)

### Show: SageMaker Console → Notebook Instance
**"The heart of our predictive capability is this SageMaker notebook that trains machine learning models on the collected data."**

#### Demo Steps:
1. **Open Notebook Instance**: `flood-prediction-notebook`
2. **Launch Jupyter**: Open the ML notebook
3. **Walk Through Key Cells**:
   - **Data Loading**: Show connection to DynamoDB tables
   - **Data Exploration**: Display visualizations of water levels and weather
   - **Feature Engineering**: Highlight lag variables, precipitation cumulative
   - **Model Training**: Random Forest classifier for flood probability
   - **Model Evaluation**: Show accuracy metrics and feature importance
   - **Model Export**: Demonstrate saving to S3

**Talking Points:**
- "Real data from our DynamoDB tables - not synthetic"
- "Model learns patterns from 2+ weeks of continuous collection"
- "Predicts flood probability 6 hours in advance"
- "Automatically exports trained model for Lambda deployment"

---

## Part 6: Model Storage - S3 Bucket (1 minute)

### Show: S3 Console → flood-prediction-models bucket
**"The trained model gets stored in S3 where our prediction Lambda can access it."**

#### Demo Steps:
1. **Navigate to S3 Bucket**: `flood-prediction-models-730335508148`
2. **Show Models Folder**: Display exported ML models
3. **Show File Details**: `flood_prediction_model.joblib` and `model_features.json`

**Talking Points:**
- "Versioned model storage for production deployment"
- "Lambda downloads model on-demand for predictions"

---

## Part 7: ML Predictions - ML Lambda (3 minutes)

### Show: AWS Lambda Console → ml-flood-predictor
**"This is where everything comes together - our ML prediction Lambda that analyzes current conditions and generates flood probability forecasts."**

#### Demo Steps:
1. **Open Lambda Function**: Show `ml-flood-predictor` function
2. **Show Code Logic**:
   - Model loading from S3
   - Recent data retrieval from DynamoDB
   - Feature engineering for prediction
   - Probability calculation and alert level determination
3. **Test Function**: Run live ML prediction
4. **Show Output**: 
   - Current flood probability percentage
   - Alert level (Normal/Watch/Warning/Emergency)
   - Timestamp and reasoning

**Talking Points:**
- "Runs every 2 hours for continuous monitoring"
- "Uses real-time data + trained ML model"
- "Generates probabilistic forecasts, not just thresholds"

---

## Part 8: Automated Alerting - SNS Integration (2 minutes)

### Show: SNS Console
**"Based on the ML predictions, the system automatically sends graduated alerts through SNS topics."**

#### Demo Steps:
1. **Show SNS Topics**:
   - `flood-alerts-emergency` (>80% probability)
   - `flood-alerts-warning` (>50% probability)  
   - `flood-alerts-watch` (>20% probability)
2. **Show Subscriptions**: Email endpoints configured
3. **Show Recent Messages**: Historical alert deliveries (don't send new ones)

**Talking Points:**
- "Graduated response based on ML confidence levels"
- "Automatic escalation ensures appropriate emergency response"
- "Email alerts to emergency management personnel"

---

## Part 9: System Monitoring - CloudWatch Dashboard (2 minutes)

### Show: CloudWatch Console → FloodMonitoringFull Dashboard
**"Finally, let's look at our operational monitoring dashboard that shows the system's health and performance."**

#### Demo Steps:
1. **Open Dashboard**: Show comprehensive metrics
2. **Highlight Key Widgets**:
   - Lambda invocation counts (data collection frequency)
   - Function performance and duration
   - Error rates (should be near zero)
   - DynamoDB usage patterns
3. **Show Time Range**: 2+ weeks of continuous operation

**Talking Points:**
- "System has been running reliably for 2+ weeks"
- "~168 data collections per day"
- "12 ML predictions per day"
- "Near-zero error rates demonstrate production readiness"

---

## Part 10: Deployment Capability (1 minute)

### Show: CloudFormation Template
**"The entire system can be replicated in any AWS account with a single CloudFormation command."**

#### Demo Steps:
1. **Show Template File**: `flood-monitoring-infrastructure.yaml`
2. **Highlight Key Sections**: Parameters, resources, outputs
3. **Show Deployment Command**: One-click deployment example

**Talking Points:**
- "Complete infrastructure as code"
- "5-10 minute deployment in fresh AWS accounts"
- "Enables rapid scaling to other regions or watersheds"

---

## Closing Summary (1 minute)

**"This demonstration shows how federal agencies can modernize emergency management through:**
- **Real inter-agency data integration** (USGS + NOAA)
- **AI/ML predictive capabilities** (6-hour advance warnings)
- **99% cost reduction** ($48K → $25/month)
- **Production-ready reliability** (2+ weeks continuous operation)
- **Rapid replication** (one-click CloudFormation deployment)

**This represents the future of federal technology collaboration - agencies working together with modern cloud and AI capabilities to enhance public safety while dramatically reducing costs."**

---

## Technical Demo Tips

### Screen Recording Setup:
- **Resolution**: 1920x1080 for clarity
- **Browser Zoom**: 125% for visibility
- **Multiple Tabs**: Pre-open all AWS console tabs
- **Test Run**: Practice transitions between services

### Demo Flow Optimization:
- **Start with Architecture**: Set context first
- **Follow Data Flow**: USGS → NOAA → DynamoDB → ML → Alerts
- **Show Real Data**: Emphasize live APIs and actual results
- **Highlight Innovation**: Inter-agency collaboration + AI/ML
- **End with Impact**: Cost savings and replication capability

### Backup Plans:
- **Screenshots**: Have key screens captured in case of connectivity issues
- **Test Data**: Ensure recent data exists in all tables
- **Function Tests**: Verify Lambdas work before recording