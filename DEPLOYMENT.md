# Deployment Guide

This guide will help you deploy the LinkedIn Skill Analysis Bot frontend to various platforms.

## Prerequisites

1. Node.js and npm installed
2. Git installed
3. Account on your chosen deployment platform (Netlify, Vercel, or GitHub Pages)

## Deployment Options

### 1. Netlify Deployment (Recommended)

1. Install Netlify CLI:
   ```bash
   npm install -g netlify-cli
   ```

2. Login to Netlify:
   ```bash
   netlify login
   ```

3. Deploy using the provided script:
   ```bash
   ./deploy.sh
   ```

   Or manually:
   ```bash
   npm run build
   netlify deploy --prod
   ```

### 2. Vercel Deployment

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy:
   ```bash
   vercel
   ```

### 3. GitHub Pages Deployment

1. Install gh-pages:
   ```bash
   npm install --save-dev gh-pages
   ```

2. Add these scripts to your `package.json`:
   ```json
   {
     "homepage": "https://yourusername.github.io/repo-name",
     "scripts": {
       "predeploy": "npm run build",
       "deploy": "gh-pages -d build"
     }
   }
   ```

3. Deploy:
   ```bash
   npm run deploy
   ```

## Environment Variables

Create a `.env` file in the frontend directory with:

```
REACT_APP_API_URL=your_backend_url
```

For production, set this to your deployed backend URL.

## CORS Configuration

After deploying, update the CORS settings in your backend (`src/main.py`) with your frontend's URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://your-netlify-app.netlify.app",  # Production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Troubleshooting

1. **CORS Issues**
   - Ensure your backend CORS settings include your frontend URL
   - Check that your API URL is correctly set in the environment variables

2. **Build Failures**
   - Clear the `build` directory: `rm -rf build`
   - Clear npm cache: `npm cache clean --force`
   - Reinstall dependencies: `npm install`

3. **Deployment Failures**
   - Check your deployment platform's logs
   - Ensure all environment variables are set
   - Verify your build command is correct

## Support

For issues or questions, please open an issue in the repository. 