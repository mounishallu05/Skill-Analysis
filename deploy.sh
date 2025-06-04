#!/bin/bash

# Build the React app
echo "Building React app..."
npm run build

# Check if Netlify CLI is installed
if ! command -v netlify &> /dev/null; then
    echo "Installing Netlify CLI..."
    npm install -g netlify-cli
fi

# Deploy to Netlify
echo "Deploying to Netlify..."
netlify deploy --prod

# Get the deployed URL
DEPLOY_URL=$(netlify deploy:list | grep "Production" | awk '{print $2}')

echo "Deployment complete!"
echo "Your app is live at: $DEPLOY_URL"
echo "Don't forget to update the CORS settings in your backend with this URL!" 