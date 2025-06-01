# Real-Time Data Pipeline with AWS Lambda and DynamoDB

## Overview
This project implements a real-time data pipeline to process tweet data using AWS services. The pipeline reads tweet data from CSV files in an S3 bucket, processes them using a Lambda function, and stores the results in a DynamoDB table. The goal is to analyze tweet sentiment and extract hashtags, storing the processed data for further analysis.

## Architecture
- **S3 Bucket**: `twitter-sentiment-raw-yourname` stores CSV files under the `raw/` prefix (e.g., `tweets_batch_0.csv`).
- **Lambda Function**: `process_tweets` processes S3 events, reads CSV files, analyzes sentiment, and writes to DynamoDB.
- **DynamoDB Table**: `tweets` stores processed tweet data with attributes: `tweet_id`, `text`, `sentiment`, `timestamp`, and `hashtags`.
- **Trigger**: S3 event notification triggers the Lambda function on new CSV uploads.

## Prerequisites
- AWS account with free-tier access.
- Python 3.9 (to match Lambda runtime).
- AWS CLI installed and configured with credentials.
- Required Python packages: `pandas==1.5.3`, `boto3`.

## Setup Instructions

### 1. Create S3 Bucket
- Create an S3 bucket named `twitter-sentiment-raw-yourname` in the `us-east-1` region.
- Upload CSV files containing tweet data to the `raw/` prefix (e.g., `tweets_batch_0.csv`).

### 2. Create DynamoDB Table
- In the DynamoDB Console, create a table named `tweets`.
- Set the partition key as `tweet_id` (String).
- Use default settings for capacity (free-tier eligible).

### 3. Prepare Lambda Function
- Navigate to `real-time-twitter-pipeline/lambda_package/`.
- Install dependencies:
  ```bash
  pip install pandas==1.5.3 boto3 -t .
	```
- Copy the Lambda function script:
  ```bash
  cp ../scripts/lambda_function.py .
  ```
- Zip the contents:
  ```bash
   zip -r ../scripts/lambda_function.zip .
  ```
- Upload the ZIP to S3: In the S3 Console, upload lambda_function.zip to s3://twitter-sentiment-raw-yourname/lambda_packages/.

### 4. Create and Configure Lambda Function
- In the Lambda Console, create a function named `process_tweets`.
- Select **Python 3.9** as the runtime.
- Upload the code from S3: `s3://twitter-sentiment-raw-yourname/lambda_packages/lambda_function.zip`.
- Set the handler to `lambda_function.lambda_handler`.
- Configure the IAM role with the following policies:
  - `AmazonS3ReadOnlyAccess`
  - `AmazonDynamoDBFullAccess`
  - `CloudWatchLogsFullAccess`
- Set **Timeout** to 15 seconds and **Memory** to 256 MB.

### 5. Set Up S3 Trigger
- In the Lambda Console, add an S3 trigger for `process_tweets`.
- Configure:
  - Bucket: `twitter-sentiment-raw-yourname`.
  - Event type: **All object create events**.
  - Prefix: `raw/`.
- Enable the trigger.

### 6. Ingest Data
- - Before running `data_ingestion.py`, ensure the S3 trigger is configured in the Lambda Console for `twitter-sentiment-raw-yourname` with prefix `raw/`.
- Run the data ingestion script to upload a random sample of tweets to S3:
  ```bash
  python scripts/ingest_data.py
  ```
- The script randomly samples 10,000 rows from data/training.1600000.processed.noemoticon.csv (using encoding='latin-1' to handle the file’s encoding), batches them into 100-row files, and uploads to s3://twitter-sentiment-raw-yourname/raw/.
- The script uses time.sleep(2) between uploads to ensure reliable triggering.
- Note: S3 triggers only process files uploaded after the trigger is created. Re-upload files if the trigger was added later.
### 7. Test the Pipeline
- Upload a sample CSV file to `s3://twitter-sentiment-raw-yourname/raw/` (e.g., `tweets_batch_0.csv`).
- In the Lambda Console, create a test event using the `S3TestEvent` template:
  ```json
  {
      "Records": [
          {
              "s3": {
                  "bucket": {
                      "name": "twitter-sentiment-raw-yourname"
                  },
                  "object": {
                      "key": "raw/tweets_batch_0.csv"
                  }
              }
          }
      ]
  }  
```
- Run the test and verify the `statusCode: 200` response.
- Check the `tweets` DynamoDB table for new items with attributes like `tweet_id`, `text`, `sentiment`, `timestamp`, and `hashtags`.
### 8. Query Sentiment Analysis
- Run the query_sentiment.py script to analyze the sentiment distribution of tweets stored in DynamoDB:
```bash
python scripts/query_sentiment.py
```
- The script queries the tweets table and calculates the percentage of positive, negative, and neutral tweets.
- Example output:
```bash
Final Sentiment Analysis:
Total Tweets: 10000
Positive Tweets: 4996 (50.0%)
Neutral Tweets: 0 (0.0%)
Negative Tweets: 5004 (50.0%)
```

## Data Format
- **Input (S3 CSV):**
  - Columns: `id`, `text`, `target`, `date`.
- **Output (DynamoDB):**
  - `tweet_id`: String (from `id`).
  - `text`: String.
  - `sentiment`: String ("positive" if `target` is 4, else "negative").
  - `timestamp`: String (from `date`).
  - `hashtags`: List of strings (extracted from `text`).

## Free Tier Usage
- **S3**: Storage within 5 GB, requests within 20,000 GETs.
- **Lambda**: Invocations within 1M requests.
- **DynamoDB**: Storage within 1 GB, 25 WCUs.
- **Billing**: Monitor the AWS Billing Dashboard to confirm no charges.

## Troubleshooting
- **Lambda Errors**: Check CloudWatch Logs for detailed error messages.
- **S3 Trigger Issues**: Ensure the prefix (`raw/`) matches and there are no overlapping event rules in S3.
- **DynamoDB Issues**: Verify the table name and region (`us-east-1`).

### Planned Upgrades
To enhance the pipeline and make it more real-world relevant, the following upgrades are planned:

- **Machine Learning Integration:** Build a machine learning model to predict tweet sentiment using the text column as input and the target column (mapped to sentiment) as the label. The model will be trained locally or on an EC2 instance to avoid SageMaker costs.
- **Flask App for Visualization and Testing:** Develop a Flask web application to serve sentiment predictions and visualize sentiment trends. The app will allow users to input new tweets and receive predicted sentiments, and it will be deployed on an EC2 instance with dynamic start/stop to manage costs.
- **Analytics and Visualizations:** Add analytics using Amazon Athena to query DynamoDB data (via export to S3) and visualize sentiment trends with Amazon QuickSight, if within the 30-day trial period.
