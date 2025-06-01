import json
import boto3
import pandas as pd

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('tweets')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    obj = s3_client.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(obj['Body'])

    for index, row in df.iterrows():
        sentiment = 'neutral' if row['target'] == 2 else 'positive' if row['target'] > 2 else 'negative'
        item = {
            'tweet_id': str(row['id']),
            'text': row['text'],
            'sentiment': sentiment,
            'timestamp': row['date'],
            'hashtags': [word for word in str(row['text']).split() if word.startswith('#')]
        }
        table.put_item(Item=item)

    return {
        'statusCode': 200,
        'body': json.dumps(f"Processed {len(df)} tweets from {key}")
    }