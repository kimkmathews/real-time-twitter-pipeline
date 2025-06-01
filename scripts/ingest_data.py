import pandas as pd
import boto3
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS credentials from .env
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)
BUCKET_NAME = 'twitter-sentiment-raw-kimkmathews'
BATCH_SIZE = 100

def upload_to_s3(df, batch_id):
    """Upload a batch of tweets to S3 as CSV."""
    file_name = f'tweets_batch_{batch_id}.csv'
    df.to_csv(file_name, index=False)
    s3_client.upload_file(file_name, BUCKET_NAME, f'raw/{file_name}')
    print(f'Uploaded {file_name} to s3://{BUCKET_NAME}/raw/')
    os.remove(file_name)

def main():
    # Load the full dataset with correct encoding and randomly sample 10,000 rows
    df_full = pd.read_csv('data/training.1600000.processed.noemoticon.csv', 
                         names=['target', 'id', 'date', 'flag', 'user', 'text'],
                         encoding='latin-1')
    df_sampled = df_full.sample(n=10000, random_state=42)  # random_state for reproducibility

    # Split into batches
    for i in range(0, len(df_sampled), BATCH_SIZE):
        batch_df = df_sampled[i:i + BATCH_SIZE]
        upload_to_s3(batch_df, i // BATCH_SIZE)
        time.sleep(1)  # Simulate real-time streaming

if __name__ == '__main__':
    main()