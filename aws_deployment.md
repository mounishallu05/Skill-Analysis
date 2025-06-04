# AWS Deployment Guide

This guide will help you deploy the LinkedIn Skill Analysis Bot to AWS.

## Prerequisites

1. AWS Account
2. AWS CLI installed and configured
3. EB CLI installed (`pip install awsebcli`)
4. Docker installed (for local testing)

## 1. Database Setup (RDS)

1. Create a PostgreSQL RDS instance:
   - Go to AWS RDS Console
   - Click "Create database"
   - Choose PostgreSQL
   - Select "Free tier" for development
   - Configure security group to allow traffic from your application
   - Note down the endpoint, username, and password

2. Update your `.env` file with RDS credentials:
```
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/dbname
```

## 2. Backend Deployment (Elastic Beanstalk)

1. Create a `Procfile` in the root directory:
```
web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

2. Create `.ebextensions/01_packages.config`:
```yaml
packages:
  yum:
    git: []
    gcc: []
    python3-devel: []
    postgresql-devel: []
```

3. Create `.ebextensions/02_python.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: src.main:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current"
```

4. Initialize EB application:
```bash
eb init -p python-3.8 linkedin-skill-analysis
```

5. Create environment:
```bash
eb create linkedin-skill-analysis-env
```

6. Deploy:
```bash
eb deploy
```

## 3. Frontend Deployment (S3 + CloudFront)

1. Build your frontend:
```bash
cd frontend
npm run build
```

2. Create an S3 bucket:
   - Go to AWS S3 Console
   - Create a new bucket
   - Enable static website hosting
   - Configure bucket policy for public access

3. Upload frontend files:
```bash
aws s3 sync build/ s3://your-bucket-name
```

4. (Optional) Set up CloudFront:
   - Create a CloudFront distribution
   - Point it to your S3 bucket
   - Configure custom domain if needed

## 4. Environment Variables

Set these environment variables in Elastic Beanstalk:
- `DATABASE_URL`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- Any other sensitive configuration

## 5. Monitoring and Maintenance

1. Set up CloudWatch alarms for:
   - CPU utilization
   - Memory usage
   - Database connections
   - Error rates

2. Configure auto-scaling if needed:
   - Set up scaling policies
   - Configure load balancer

## 6. Security Considerations

1. Use AWS Secrets Manager for sensitive data
2. Configure security groups properly
3. Enable HTTPS everywhere
4. Set up AWS WAF if needed
5. Regular security updates

## Troubleshooting

1. Check EB logs:
```bash
eb logs
```

2. SSH into instance:
```bash
eb ssh
```

3. Common issues:
   - Database connection issues: Check security groups
   - Memory issues: Adjust instance type
   - Deployment failures: Check Procfile and requirements.txt

## Cost Optimization

1. Use reserved instances for production
2. Enable auto-scaling
3. Use appropriate instance types
4. Monitor and clean up unused resources

## Backup and Recovery

1. Set up automated RDS backups
2. Configure S3 versioning
3. Document recovery procedures
4. Test backup restoration regularly 