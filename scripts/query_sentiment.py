import boto3
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

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb',
                         aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,
                         region_name=aws_region)
table = dynamodb.Table('tweets')

def analyze_sentiment():
    # Scan the table to count sentiments
    response = table.scan()
    items = response['Items']

    positive_count = sum(1 for item in items if item['sentiment'] == 'positive')
    neutral_count = sum(1 for item in items if item['sentiment'] == 'neutral')
    negative_count = sum(1 for item in items if item['sentiment'] == 'negative')
    total = len(items)

    print(f"Sentiment Analysis Results:")
    print(f"Total Tweets: {total}")
    print(f"Positive Tweets: {positive_count} ({positive_count/total*100:.1f}%)")
    print(f"Neutral Tweets: {neutral_count} ({neutral_count/total*100:.1f}%)")
    print(f"Negative Tweets: {negative_count} ({negative_count/total*100:.1f}%)")

    # Paginate if there are more items
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])
        positive_count = sum(1 for item in items if item['sentiment'] == 'positive')
        neutral_count = sum(1 for item in items if item['sentiment'] == 'neutral')
        negative_count = sum(1 for item in items if item['sentiment'] == 'negative')
        total = len(items)

    return positive_count, neutral_count, negative_count, total

if __name__ == "__main__":
    positive, neutral, negative, total = analyze_sentiment()
    print(f"\nFinal Sentiment Analysis:")
    print(f"Total Tweets: {total}")
    print(f"Positive Tweets: {positive} ({positive/total*100:.1f}%)")
    print(f"Neutral Tweets: {neutral} ({neutral/total*100:.1f}%)")
    print(f"Negative Tweets: {negative} ({negative/total*100:.1f}%)")