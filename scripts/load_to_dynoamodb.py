import boto3
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve AWS credentials from environment variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')

# Validate credentials
if not aws_access_key_id or not aws_secret_access_key or not aws_region:
    raise ValueError("Missing required environment variables in .env file")

# Initialize S3 and DynamoDB clients
s3_client = boto3.client('s3',
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        region_name=aws_region)
dynamodb = boto3.resource('dynamodb',
                         aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,
                         region_name=aws_region)
table = dynamodb.Table('tweets')

def process_s3_file(bucket, key):
    print(f"Processing {key}...")
    # Download the file from S3
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    # Read the CSV into a pandas DataFrame
    df = pd.read_csv(obj['Body'])
    # Process each row and write to DynamoDB
    for _, row in df.iterrows():
        table.put_item(Item={
            'tweet_id': str(row['id']),
            'text': row['text'],
            'sentiment': 'positive' if row['target'] == 4 else 'negative',
            'timestamp': row['date'],
            'hashtags': [word for word in str(row['text']).split() if word.startswith('#')]
        })
    print(f"Loaded {len(df)} tweets from {key} into DynamoDB")

# Process all files in S3 raw/ prefix
bucket = 'twitter-sentiment-raw-kimkmathews'
prefix = 'raw/'
response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
if 'Contents' in response:
    for obj in response['Contents']:
        key = obj['Key']
        if key.endswith('.csv'):
            process_s3_file(bucket, key)
else:
    print("No CSV files found in S3 bucket under raw/ prefix")