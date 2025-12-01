import json
import boto3
import os
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

## Lambda function for searching photos using natural language

# Initialize AWS clients
lex_client = boto3.client('lexv2-runtime')

# OpenSearch configuration
ES_HOST = os.environ.get('ES_HOST', '')
ES_REGION = os.environ.get('ES_REGION', 'us-east-1')
ES_INDEX = 'photos'

# Lex Bot configuration
LEX_BOT_ID = os.environ.get('LEX_BOT_ID', '')
LEX_BOT_ALIAS_ID = os.environ.get('LEX_BOT_ALIAS_ID', '')
LEX_LOCALE_ID = os.environ.get('LEX_LOCALE_ID', 'en_US')

def get_keywords(inputstr):
    """
    Use Amazon Lex to extract keywords from natural language query.
    Falls back to simple word splitting if Lex is not available.
    """
    print(f"Getting keywords from: {inputstr}")
    
    try:
        # Try using Lex V2
        if LEX_BOT_ID and LEX_BOT_ALIAS_ID:
            print("Using Lex for keyword extraction")
            response = lex_client.recognize_text(
                botId=LEX_BOT_ID,
                botAliasId=LEX_BOT_ALIAS_ID,
                localeId=LEX_LOCALE_ID,
                sessionId='search-photos-session',
                text=inputstr
            )
            
            print(f"Lex response: {json.dumps(response, default=str)}")
            
            keywords = []
            if 'sessionState' in response and 'intent' in response['sessionState']:
                slots = response['sessionState']['intent'].get('slots', {})
                keywords = [v['value']['interpretedValue'].lower() for k, v in slots.items() if v and 'value' in v]
            
            if keywords:
                print(f"Lex returned keywords: {keywords}")
                return keywords
    
    except Exception as e:
        print(f"Error calling Lex: {str(e)}")
    
    # Fallback: simple keyword extraction
    print("Using fallback keyword extraction")
    stop_words = {'show', 'me', 'photos', 'photo', 'with', 'of', 'in', 'the', 'a', 'an', 'and', 'or', 'find'}
    keywords = [word.lower() for word in inputstr.split() if word.lower() not in stop_words]
    print(f"Extracted keywords: {keywords}")
    return keywords

def get_image_locations(keywords):
    """Search OpenSearch for photos matching the keywords"""
    print(f"Searching for images with keywords: {keywords}")
    
    if not keywords:
        print("No keywords provided")
        return []
    
    try:
        # Create OpenSearch client with AWS authentication
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
        
        # Build the search query
        prepared_q = []
        for k in keywords:
            prepared_q.append({"match": {"labels": k}})
        
        q = {
            "query": {
                "bool": {
                    "should": prepared_q,
                    "minimum_should_match": 1
                }
            },
            "size": 100
        }
        
        print(f"OpenSearch query: {json.dumps(q)}")
        
        # Execute search
        r = client.search(index=ES_INDEX, body=q)
        print(f"OpenSearch response: {json.dumps(r)}")
        
        # Format results
        image_array = []
        for each in r['hits']['hits']:
            objectKey = each['_source']['objectKey']
            bucket = each['_source']['bucket']
            image_url = f"https://{bucket}.s3.amazonaws.com/{objectKey}"
            labels = each['_source'].get('labels', [])
            
            image_array.append({
                'url': image_url,
                'labels': labels
            })
            print(f"Found image with labels: {labels}")
        
        print(f"Total images found: {len(image_array)}")
        return image_array
        
    except Exception as e:
        print(f"Error searching OpenSearch: {str(e)}")
        return []

def lambda_handler(event, context):
    """
    Lambda function to search photos based on natural language query.
    """
    print(f"Received event: {json.dumps(event)}")
    
    # Extract query parameter from API Gateway event
    inputText = None
    if 'queryStringParameters' in event and event['queryStringParameters']:
        inputText = event['queryStringParameters'].get('q', '')
    elif 'params' in event and 'querystring' in event['params']:
        inputText = event['params']['querystring'].get('q', '')
    
    if not inputText:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps({
                'results': [],
                'message': 'No query provided'
            })
        }
    
    print(f"Search query: {inputText}")
    
    # Get keywords from the query using Lex
    keywords = get_keywords(inputText)
    print(f"Keywords: {keywords}")
    
    # Search for images using the keywords
    image_array = get_image_locations(keywords)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True
        },
        'body': json.dumps({
            'results': image_array
        })
    }
