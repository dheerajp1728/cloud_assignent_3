import json
import boto3
import os
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# Initialize AWS clients
lex_client = boto3.client('lexv2-runtime')

# ElasticSearch/OpenSearch configuration
ES_HOST = os.environ.get('ES_HOST', '')
ES_REGION = os.environ.get('ES_REGION', 'us-east-1')
ES_INDEX = 'photos'

# Lex Bot configuration
LEX_BOT_ID = os.environ.get('LEX_BOT_ID', '')
LEX_BOT_ALIAS_ID = os.environ.get('LEX_BOT_ALIAS_ID', '')
LEX_LOCALE_ID = os.environ.get('LEX_LOCALE_ID', 'en_US')

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

def disambiguate_query(query):
    """
    Use Amazon Lex to disambiguate the search query and extract keywords.
    """
    print(f"Disambiguating query with Lex: {query}")
    
    try:
        response = lex_client.recognize_text(
            botId=LEX_BOT_ID,
            botAliasId=LEX_BOT_ALIAS_ID,
            localeId=LEX_LOCALE_ID,
            sessionId='search-session',
            text=query
        )
        
        print(f"Lex response: {json.dumps(response, default=str)}")
        
        # Extract slots/keywords from Lex response
        keywords = []
        
        if 'sessionState' in response and 'intent' in response['sessionState']:
            slots = response['sessionState']['intent'].get('slots', {})
            
            # Extract keyword values from slots
            for slot_name, slot_value in slots.items():
                if slot_value and 'value' in slot_value:
                    keyword = slot_value['value']['interpretedValue']
                    if keyword:
                        keywords.append(keyword.lower())
        
        print(f"Extracted keywords: {keywords}")
        return keywords
        
    except Exception as e:
        print(f"Error calling Lex: {str(e)}")
        # Fallback: split query by common words and use as keywords
        stop_words = {'show', 'me', 'photos', 'with', 'of', 'in', 'the', 'a', 'an', 'and', 'or'}
        keywords = [word.lower() for word in query.split() if word.lower() not in stop_words]
        print(f"Fallback keywords: {keywords}")
        return keywords

def search_photos(keywords):
    """
    Search for photos in OpenSearch using the provided keywords.
    """
    if not keywords:
        print("No keywords provided")
        return []
    
    print(f"Searching for photos with keywords: {keywords}")
    
    try:
        es_client = get_opensearch_client()
        
        # Build the search query - match any of the keywords in labels
        should_clauses = [{'match': {'labels': keyword}} for keyword in keywords]
        
        query = {
            'query': {
                'bool': {
                    'should': should_clauses,
                    'minimum_should_match': 1
                }
            },
            'size': 100
        }
        
        print(f"OpenSearch query: {json.dumps(query)}")
        
        response = es_client.search(
            index=ES_INDEX,
            body=query
        )
        
        print(f"OpenSearch response: {json.dumps(response)}")
        
        # Format the results
        results = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            photo = {
                'url': f"https://{source['bucket']}.s3.amazonaws.com/{source['objectKey']}",
                'labels': source.get('labels', [])
            }
            results.append(photo)
        
        print(f"Found {len(results)} results")
        return results
        
    except Exception as e:
        print(f"Error searching OpenSearch: {str(e)}")
        return []

def lambda_handler(event, context):
    """
    Lambda function to search photos based on natural language query.
    """
    print(f"Received event: {json.dumps(event)}")
    
    # Extract query parameter
    query = None
    if 'queryStringParameters' in event and event['queryStringParameters']:
        query = event['queryStringParameters'].get('q', '')
    
    if not query:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': json.dumps({
                'results': [],
                'message': 'No query provided'
            })
        }
    
    print(f"Search query: {query}")
    
    # Disambiguate query using Lex
    keywords = disambiguate_query(query)
    
    # Search for photos
    results = search_photos(keywords)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        },
        'body': json.dumps({
            'results': results
        })
    }
