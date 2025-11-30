# GitHub Actions CI/CD Setup Guide

## Overview
This project uses GitHub Actions to automate Lambda and frontend deployments to AWS.

## Setup Steps

### 1. Configure AWS Credentials in GitHub

Go to your repository settings: https://github.com/dheerajp1728/cloud_assignent_3/settings/secrets/actions

Add these secrets:
- **AWS_ACCESS_KEY_ID**: Your AWS access key
- **AWS_SECRET_ACCESS_KEY**: Your AWS secret key

### 2. Get AWS Credentials

Run this command to get your AWS credentials:
```powershell
aws iam create-access-key --user-name your-username
```

Or create them in AWS Console:
1. Go to IAM → Users → Your User
2. Security credentials → Create access key
3. Choose "CLI" as use case
4. Copy Access Key ID and Secret Access Key

### 3. Add Secrets to GitHub

```bash
# In GitHub repository settings:
Settings → Secrets and variables → Actions → New repository secret

Name: AWS_ACCESS_KEY_ID
Value: <your-access-key-id>

Name: AWS_SECRET_ACCESS_KEY
Value: <your-secret-access-key>
```

### 4. Workflow Triggers

The workflow automatically runs when:
- ✅ Code is pushed to `main` branch
- ✅ Pull request is created to `main` branch
- ✅ Manually triggered via "Actions" tab

### 5. Manual Trigger

1. Go to: https://github.com/dheerajp1728/cloud_assignent_3/actions
2. Select "Deploy AI Photo Search Application"
3. Click "Run workflow"
4. Select branch: `main`
5. Click "Run workflow"

## Workflow Jobs

### Job 1: Deploy Lambda Functions
- Installs Python dependencies
- Packages Lambda functions with dependencies
- Deploys to AWS Lambda

### Job 2: Deploy Frontend
- Uploads frontend to S3
- Sets proper content type
- Runs after Lambda deployment

### Job 3: Test Deployment
- Verifies Lambda functions exist
- Verifies frontend is deployed
- Shows deployment summary

## Customize Workflow

Edit `.github/workflows/deploy.yml` to modify:

```yaml
env:
  AWS_REGION: us-east-1                                    # Change region
  LAMBDA_INDEX_FUNCTION: ai-photo-search-index-photos     # Change function name
  LAMBDA_SEARCH_FUNCTION: ai-photo-search-search-photos   # Change function name
  FRONTEND_BUCKET: ai-photo-search-frontend-381437599887  # Change bucket name
```

## Development Workflow

### Option 1: Automatic Deployment (Recommended)
```powershell
# Make changes to code
git add .
git commit -m "Update Lambda function"
git push origin main
# GitHub Actions automatically deploys!
```

### Option 2: Pull Request Workflow
```powershell
# Create feature branch
git checkout -b feature/new-feature

# Make changes
git add .
git commit -m "Add new feature"
git push origin feature/new-feature

# Create Pull Request on GitHub
# GitHub Actions runs tests
# Merge PR to trigger deployment
```

### Option 3: Manual Deployment
1. Go to Actions tab
2. Click "Deploy AI Photo Search Application"
3. Click "Run workflow"

## Monitoring

View workflow runs:
- https://github.com/dheerajp1728/cloud_assignent_3/actions

Each run shows:
- ✅ Success/Failure status
- ⏱️ Execution time
- 📝 Detailed logs for each step
- 🔍 Error messages if failed

## Advanced: Add Testing

Create `.github/workflows/test.yml`:

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install pytest boto3 moto
      - name: Run tests
        run: |
          pytest tests/
```

## Troubleshooting

### Error: "Unable to locate credentials"
- ✅ Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set in GitHub Secrets

### Error: "AccessDenied"
- ✅ Ensure IAM user has permissions for Lambda and S3

### Error: "Function not found"
- ✅ Update function names in workflow env variables

### Workflow not triggering
- ✅ Check `.github/workflows/deploy.yml` is in main branch
- ✅ Verify workflow is enabled in Actions tab

## IAM Permissions Required

Your AWS user needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:UpdateFunctionCode",
        "lambda:GetFunction",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:lambda:us-east-1:381437599887:function:ai-photo-search-*",
        "arn:aws:s3:::ai-photo-search-frontend-381437599887",
        "arn:aws:s3:::ai-photo-search-frontend-381437599887/*"
      ]
    }
  ]
}
```

## Benefits of GitHub Actions

✅ **Automatic Deployment**: Push code and it's deployed automatically
✅ **Consistent Builds**: Same environment every time
✅ **Parallel Jobs**: Lambda and frontend deploy simultaneously
✅ **Built-in Testing**: Verify deployment after each run
✅ **History**: See all deployments and rollback if needed
✅ **Free**: 2,000 minutes/month for public repos
