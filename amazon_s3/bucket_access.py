import os

from dotenv import load_dotenv
import boto3
import botocore


def update_manifest():
  '''Update the manifest file in the S3 bucket'''

  # Load environment variables
  load_dotenv()

  # Create authenticated S3 client
  s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY'],
    aws_secret_access_key=os.environ['AWS_SECRET_KEY'],
    region_name='eu-west-3'
  )

  # Fetch the file
  bucket     = 'arxiv'
  file_key   = 'src/arXiv_src_manifest.xml'
  local_file = 'amazon_s3/arXiv_src_manifest.xml'
  try:
    response = s3.get_object(Bucket=bucket, Key=file_key, RequestPayer='requester')
    with open(local_file, 'wb') as f:
        f.write(response['Body'].read())
    print(f"Saved manifest to: {local_file}")
  except botocore.exceptions.ClientError as e:
    print(f"Failed to download manifest: {e}")


def download_source_tarball(source_file):
  '''Download the source tarball from the S3 bucket'''

  # Load environment variables
  load_dotenv()

  # Create authenticated S3 client
  s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY'],
    aws_secret_access_key=os.environ['AWS_SECRET_KEY'],
    region_name='eu-west-3'
  )

  # Fetch the file
  bucket     = 'arxiv'
  file_key   = f'src/{source_file}'
  local_file = f'amazon_s3/files/{source_file}'
  try:
    response = s3.get_object(Bucket=bucket, Key=file_key, RequestPayer='requester')
    os.makedirs('files', exist_ok=True)
    with open(local_file, 'wb') as f:
        f.write(response['Body'].read())
    print(f"Source tarball saved to: {local_file}")
  except botocore.exceptions.ClientError as e:
    print(f"Failed to download the tarball: {e}")

download_source_tarball('arXiv_src_0001_001.tar')
