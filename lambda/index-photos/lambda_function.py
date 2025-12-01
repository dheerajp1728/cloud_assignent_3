import json
import boto3
import os
from datetime import datetime
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

## Lambda function for indexing photos with Rekognition labels

# Initialize AWS clients
s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')

# OpenSearch configuration
ES_HOST = os.environ.get('ES_HOST', '')
ES_REGION = os.environ.get('ES_REGION', 'us-east-1')
ES_INDEX = 'photos'

def detect_labels(photo, bucket):
    """Detect labels using Rekognition and get custom labels from S3 metadata"""
    labels_res = []
    
    print(f'Detecting labels for {photo}')
    
    # Use Rekognition to detect labels
    response = rekognition_client.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MaxLabels=10,
        MinConfidence=70
    )
    
    # Extract label names
    for label in response['Labels']:
        print(f"Label: {label['Name']}")
        labels_res.append(label['Name'].lower())
    
    # Get custom labels from S3 metadata
    try:
        im_metadata = s3_client.head_object(Bucket=bucket, Key=photo)
        
        if 'Metadata' in im_metadata and len(im_metadata['Metadata']) != 0:
            if 'customlabels' in im_metadata['Metadata']:
                user_labels = im_metadata['Metadata']['customlabels'].split(",")
                user_labels = [label.strip().lower() for label in user_labels if label.strip()]
                labels_res.extend(user_labels)
                print(f"Custom labels: {user_labels}")
    except Exception as e:
        print(f"Error getting metadata: {str(e)}")
    
    return labels_res

def index_into_es(index, doc_type, new_doc):
    """Index document into OpenSearch"""
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
    
    response = client.index(
        index=index,
        body=json.loads(new_doc),
        refresh=True
    )
    print(f"OpenSearch response: {response}")
    print("Index operation successful!")
    return response

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
        image_name = record['s3']['object']['key']
        
        print(f"Processing image: {image_name} from bucket: {bucket}")
        
        try:
            # Detect labels using Rekognition and get custom labels
            labels_res = detect_labels(image_name, bucket)
            print(f"Labels result ==> {labels_res}")
            
            # Create timestamp in ISO 8601 format for OpenSearch
            created_timestamp = datetime.now().isoformat()
            
            # Create the document to index
            query = {
                'objectKey': image_name,
                'bucket': bucket,
                'createdTimestamp': created_timestamp,
                'labels': labels_res
            }
            
            # Index into OpenSearch
            index_into_es(ES_INDEX, 'photo', json.dumps(query))
            
            print("Processing completed successfully")
            
        except Exception as e:
            print(f"Error processing {image_name}: {str(e)}")
            raise e
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda! Photo indexed successfully.')
    }
