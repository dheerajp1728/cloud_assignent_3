import json
import boto3
import os
from datetime import datetime
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# Initialize AWS clients
s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')

# ElasticSearch/OpenSearch configuration
ES_HOST = os.environ.get('ES_HOST', '')
ES_REGION = os.environ.get('ES_REGION', 'us-east-1')
ES_INDEX = 'photos'

def get_opensearch_client():
    """Create and return an OpenSearch client with AWS authentication"""
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        ES_REGION,
        'es',
        session_token=credentials.token
    )
    
    client = OpenSearch(
        hosts=[{'host': ES_HOST, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    return client

def lambda_handler(event, context):
    """
    Lambda function to index photos when uploaded to S3.
    Triggered by S3 PUT events.
    """
    print(f"Received event: {json.dumps(event)}")
    
    # Parse S3 event
    for record in event['Records']:
        # Get bucket and object key from the event
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        print(f"Processing: bucket={bucket}, key={key}")
        
        try:
            # Get object metadata from S3
            response = s3_client.head_object(Bucket=bucket, Key=key)
            metadata = response.get('Metadata', {})
            
            print(f"S3 Metadata: {metadata}")
            
            # Get custom labels from metadata
            custom_labels = []
            if 'customlabels' in metadata:
                # Parse comma-separated custom labels
                custom_labels_str = metadata['customlabels']
                custom_labels = [label.strip() for label in custom_labels_str.split(',') if label.strip()]
            
            print(f"Custom labels: {custom_labels}")
            
            # Detect labels using Rekognition
            rekognition_response = rekognition_client.detect_labels(
                Image={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': key
                    }
                },
                MaxLabels=10,
                MinConfidence=70
            )
            
            # Extract label names from Rekognition response
            rekognition_labels = [label['Name'].lower() for label in rekognition_response['Labels']]
            print(f"Rekognition labels: {rekognition_labels}")
            
            # Combine custom labels and Rekognition labels
            all_labels = custom_labels + rekognition_labels
            # Remove duplicates while preserving order
            all_labels = list(dict.fromkeys(all_labels))
            
            print(f"All labels: {all_labels}")
            
            # Create timestamp
            created_timestamp = datetime.now().isoformat()
            
            # Create the document to index
            document = {
                'objectKey': key,
                'bucket': bucket,
                'createdTimestamp': created_timestamp,
                'labels': all_labels
            }
            
            print(f"Document to index: {json.dumps(document)}")
            
            # Index the document in OpenSearch
            es_client = get_opensearch_client()
            response = es_client.index(
                index=ES_INDEX,
                body=document,
                refresh=True
            )
            
            print(f"OpenSearch response: {json.dumps(response)}")
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Photo indexed successfully',
                    'objectKey': key,
                    'labels': all_labels
                })
            }
            
        except Exception as e:
            print(f"Error processing {key}: {str(e)}")
            raise e
    
    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete')
    }
