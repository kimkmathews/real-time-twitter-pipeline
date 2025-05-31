import json
import boto3
import pandas as pd
import io
import re

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('tweets')

def extract_hashtags(text):
    """Extract hashtags from tweet text."""
    return [word for word in text.split() if word.startswith('#')]

def lambda_handler(event, context):
    """Process S3 CSV and write to DynamoDB."""
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        # Read CSV from S3
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(io.BytesIO(obj['Body'].read()))
        
        # Process each tweet
        for _, row in df.iterrows():
            hashtags = extract_hashtags(row['text'])
            table.put_item(
                Item={
                    'tweet_id': str(row['id']),
                    'text': row['text'],
                    'sentiment': 'positive' if row['target'] == 4 else 'negative',
                    'timestamp': row['date'],
                    'hashtags': hashtags
                }
            )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Processed tweets successfully')
    }