# 📷 AI Photo Search Application

A serverless photo album application powered by AWS services that allows users to search for photos using natural language queries and automatically indexes photos using AI-powered label detection.

[![AWS](https://img.shields.io/badge/AWS-Cloud-orange)](https://aws.amazon.com)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🌟 Features

- **🔍 Natural Language Search**: Search photos using everyday language like "show me dogs" or "find cats"
- **🤖 AI-Powered Labels**: Automatic label detection using Amazon Rekognition
- **📤 Easy Upload**: Drag-and-drop photo upload with optional custom labels
- **⚡ Serverless Architecture**: Built entirely on AWS serverless services
- **🔄 Auto-Indexing**: Photos are automatically indexed upon upload
- **💬 Smart Query Processing**: Enhanced with Amazon Lex for natural language understanding
- **🎨 Responsive UI**: Clean, modern interface that works on all devices

## 🚀 Live Demo

**Frontend Application:** http://ai-photo-search-frontend-381437599887.s3-website-us-east-1.amazonaws.com

**API Endpoint:** https://ur2wyo21r1.execute-api.us-east-1.amazonaws.com/prod

## 📋 Table of Contents

- [Architecture](#architecture)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [Contributing](#contributing)

## 🏗️ Architecture

```
┌──────────────┐
│   User       │
│   Browser    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│  S3 Static Website Hosting   │
│  (Frontend)                  │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  API Gateway                 │
│  • GET /search?q={query}     │
│  • PUT /upload/{filename}    │
└──────┬──────────────┬────────┘
       │              │
       ▼              ▼
┌─────────────┐   ┌──────────┐
│  Lambda     │   │  S3      │
│  (Search)   │   │  Proxy   │
└──────┬──────┘   └────┬─────┘
       │               │
       ▼               ▼
┌─────────────┐   ┌──────────────┐
│ OpenSearch  │   │  S3 Photos   │
│ (Index)     │   │  Bucket      │
└─────────────┘   └──────┬───────┘
                         │
                         ▼
                  ┌─────────────┐
                  │  Lambda     │
                  │  (Index)    │
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ Rekognition │
                  └─────────────┘
```

## 🛠️ Technologies Used

### AWS Services
- **Lambda**: Serverless compute for photo indexing and search
- **API Gateway**: RESTful API endpoints
- **S3**: Photo storage and static website hosting
- **Rekognition**: AI-powered image analysis and label detection
- **OpenSearch**: Fast, scalable search engine for photo metadata
- **Lex**: Natural language understanding for query processing
- **CloudFormation**: Infrastructure as Code
- **CodePipeline**: CI/CD automation (optional)
- **IAM**: Security and access management

### Frontend
- **HTML5/CSS3**: Modern, responsive UI
- **JavaScript**: Client-side logic
- **API Gateway SDK**: Generated JavaScript SDK for API calls

### Backend
- **Python 3.11**: Lambda function runtime
- **Boto3**: AWS SDK for Python

## 🎯 Getting Started

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Python 3.11 or later
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/dheerajp1728/cloud_assignent_3.git
   cd cloud_assignent_3
   ```

2. **Deploy the infrastructure**
   
   Using CloudFormation:
   ```bash
   aws cloudformation create-stack \
     --stack-name ai-photo-search-stack \
     --template-body file://cloudformation/stack.yaml \
     --capabilities CAPABILITY_NAMED_IAM \
     --region us-east-1
   ```

3. **Configure the Lambda trigger**
   ```bash
   aws s3api put-bucket-notification-configuration \
     --bucket ai-photo-search-photos-{AccountId} \
     --notification-configuration file://s3-notification-config.json
   ```

4. **Upload the frontend**
   ```bash
   aws s3 cp frontend/index.html s3://ai-photo-search-frontend-{AccountId}/ \
     --region us-east-1
   ```

5. **Access the application**
   
   Open: `http://ai-photo-search-frontend-{AccountId}.s3-website-us-east-1.amazonaws.com`

## 💡 Usage

### Searching Photos

1. Enter a search query using natural language:
   - Simple: `dog`, `cat`, `tree`
   - Natural: `show me dogs`, `find animals`
   - Complex: `cats and trees`

2. Click **Search** or press Enter

3. View results in a grid layout with detected labels

### Uploading Photos

1. Click **Choose File** or drag-and-drop a photo
2. (Optional) Add custom labels separated by commas
   - Example: `vacation, beach, sunset, family`
3. Click **Upload Photo**
4. Wait 5-10 seconds for automatic indexing
5. Search for your photo using detected or custom labels

## 📚 API Documentation

### Authentication

All API requests require an API key sent via the `x-api-key` header.

**API Key:** `EFFxLhQZQC5PmtAZww5953OrhluY72A2bNZAVFG4`

### Endpoints

#### Search Photos

```http
GET /search?q={query}
```

**Parameters:**
- `q` (required): Search query string

**Response:**
```json
{
  "results": [
    {
      "url": "https://bucket.s3.amazonaws.com/photo.jpg",
      "labels": ["dog", "pet", "animal", "canine"]
    }
  ]
}
```

**Example:**
```bash
curl -X GET "https://ur2wyo21r1.execute-api.us-east-1.amazonaws.com/prod/search?q=dog" \
  -H "x-api-key: EFFxLhQZQC5PmtAZww5953OrhluY72A2bNZAVFG4"
```

#### Upload Photo

```http
PUT /upload/{filename}
```

**Parameters:**
- `filename` (required): Name of the file to upload

**Headers:**
- `Content-Type`: Image MIME type (e.g., `image/jpeg`)
- `x-amz-meta-customLabels` (optional): Comma-separated custom labels

**Example:**
```bash
curl -X PUT "https://ur2wyo21r1.execute-api.us-east-1.amazonaws.com/prod/upload/photo.jpg" \
  -H "x-api-key: EFFxLhQZQC5PmtAZww5953OrhluY72A2bNZAVFG4" \
  -H "Content-Type: image/jpeg" \
  -H "x-amz-meta-customLabels: vacation, beach, sunset" \
  --data-binary @photo.jpg
```

## 🚢 Deployment

### Manual Deployment

See [Getting Started](#getting-started) for step-by-step instructions.

### CI/CD with CodePipeline

To enable automatic deployments:

1. Create a GitHub Personal Access Token
2. Deploy the Lambda pipeline:
   ```bash
   aws cloudformation create-stack \
     --stack-name ai-photo-search-lambda-pipeline \
     --template-body file://codepipeline/codepipeline-lambda.yaml \
     --parameters ParameterKey=GitHubToken,ParameterValue=your_token_here \
     --capabilities CAPABILITY_NAMED_IAM
   ```

3. Deploy the frontend pipeline:
   ```bash
   aws cloudformation create-stack \
     --stack-name ai-photo-search-frontend-pipeline \
     --template-body file://codepipeline/codepipeline-frontend.yaml \
     --parameters ParameterKey=GitHubToken,ParameterValue=your_token_here \
     --capabilities CAPABILITY_NAMED_IAM
   ```

See `codepipeline/DEPLOYMENT_INSTRUCTIONS.md` for detailed instructions.

## ⚙️ Configuration

### Environment Variables

Lambda functions use the following environment variables:

**index-photos Lambda:**
- `OPENSEARCH_ENDPOINT`: OpenSearch domain endpoint
- `OPENSEARCH_INDEX`: Index name (default: `photos`)

**search-photos Lambda:**
- `OPENSEARCH_ENDPOINT`: OpenSearch domain endpoint
- `OPENSEARCH_INDEX`: Index name (default: `photos`)
- `LEX_BOT_ID`: Amazon Lex bot ID (optional)
- `LEX_BOT_ALIAS_ID`: Amazon Lex bot alias ID (optional)

### Frontend Configuration

Update `frontend/index.html` with your API details:

```javascript
const API_GATEWAY_URL = 'https://your-api-id.execute-api.region.amazonaws.com/prod';
const API_KEY = 'your-api-key-here';
```

## 📁 Project Structure

```
.
├── api/                          # API Gateway configuration
│   ├── sdk/                      # Generated API SDK
│   ├── swagger.yaml              # API specification
│   └── API_DOCUMENTATION.md      # API documentation
├── cloudformation/               # Infrastructure as Code
│   ├── stack.yaml                # Main CloudFormation template
│   └── CLOUDFORMATION_GUIDE.md   # Deployment guide
├── codepipeline/                 # CI/CD pipelines
│   ├── codepipeline-lambda.yaml  # Lambda deployment pipeline
│   └── codepipeline-frontend.yaml # Frontend deployment pipeline
├── frontend/                     # Web application
│   ├── index.html                # Main HTML file
│   ├── buildspec.yml             # CodeBuild specification
│   └── sdk/                      # API Gateway SDK
├── lambda/                       # Lambda functions
│   ├── index-photos/             # Photo indexing function
│   │   ├── lambda_function.py
│   │   └── buildspec.yml
│   └── search-photos/            # Search function
│       ├── lambda_function.py
│       └── buildspec.yml
├── lex/                          # Amazon Lex bot configuration
│   ├── bot-config.json
│   ├── intent-config.json
│   └── README.md
└── README.md                     # This file
```

## 🔐 Security

- API Gateway requires API key authentication
- S3 buckets use IAM policies for access control
- Lambda functions follow least privilege principle
- OpenSearch domain uses VPC security groups
- CloudFormation templates include security best practices

## 🧪 Testing

### Test Search Functionality

```bash
curl -X GET "https://ur2wyo21r1.execute-api.us-east-1.amazonaws.com/prod/search?q=test" \
  -H "x-api-key: EFFxLhQZQC5PmtAZww5953OrhluY72A2bNZAVFG4"
```

### Test Upload Functionality

```bash
curl -X PUT "https://ur2wyo21r1.execute-api.us-east-1.amazonaws.com/prod/upload/test.jpg" \
  -H "x-api-key: EFFxLhQZQC5PmtAZww5953OrhluY72A2bNZAVFG4" \
  -H "Content-Type: image/jpeg" \
  --data-binary @test.jpg
```

## 📊 Performance

- **Search Latency**: < 1 second
- **Upload Processing**: 5-10 seconds (including Rekognition)
- **Indexing Delay**: Near real-time (< 10 seconds)
- **Concurrent Uploads**: Scales automatically with Lambda
- **Storage**: Unlimited (S3)

## 💰 Cost Estimation

Estimated monthly costs (after free tier):

- **Lambda**: ~$0.20 per 1 million requests
- **API Gateway**: ~$3.50 per 1 million requests
- **S3**: ~$0.023 per GB stored
- **Rekognition**: ~$1.00 per 1,000 images
- **OpenSearch**: ~$13.00 per month (t2.small.search)
- **CodePipeline**: ~$1.00 per pipeline per month (optional)

**Total**: ~$20-25/month for moderate usage

## 🐛 Troubleshooting

### Upload Not Working

**Issue:** Upload fails with AccessDenied error

**Solution:** Check IAM permissions on APIGatewayS3ProxyRole
```bash
aws iam get-role-policy --role-name APIGatewayS3ProxyRole --policy-name S3PutObjectPolicy
```

### Search Returns No Results

**Issue:** Photos uploaded but not appearing in search

**Solution:** 
1. Check Lambda trigger is configured on S3 bucket
2. View CloudWatch logs for index-photos Lambda
3. Verify OpenSearch domain is accessible

### Frontend Not Loading

**Issue:** Frontend shows blank page or 404

**Solution:**
1. Verify S3 bucket has static website hosting enabled
2. Check bucket policy allows public read access
3. Ensure index.html is uploaded to bucket root

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributors

- **Dheeraj Patel** - Initial work - [dheerajp1728](https://github.com/dheerajp1728)

## 🙏 Acknowledgments

- AWS for providing the cloud infrastructure
- Amazon Rekognition for AI-powered image analysis
- Amazon Lex for natural language understanding
- OpenSearch for fast and scalable search capabilities

## 📧 Support

For questions or issues, please open an issue on GitHub or contact the maintainers.

---

**Built with ❤️ using AWS Serverless Technologies**
