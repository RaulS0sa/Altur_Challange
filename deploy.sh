#!/bin/bash

# Configuration
APP_NAME="altur-challenge-app"
GROQ_KEY="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"
DEEPGRAM_KEY="1e7306fd01c9a70b28ffca2c0b5893213e9a0085"
SECRET="django-insecure-x3^@q*v#v465q-@eyk&ru6#qeca&sw_!hk%lb4407^4#q1#ftj"

echo "🚀 Starting Deployment for $APP_NAME..."

# 1. Set Config Vars
echo "🔑 Setting environment variables..."
heroku config:set GROQ_API_KEY="$GROQ_KEY" --app $APP_NAME
heroku config:set DEEPGRAM_API_KEY="$DEEPGRAM_KEY" --app $APP_NAME
heroku config:set DEBUG=False --app $APP_NAME
heroku config:set SECRET_KEY="$SECRET" --app $APP_NAME

# 2. Push code
echo "📤 Pushing code to Heroku..."
git add --all
git commit -m "Fix requirements, static files, and nested paths $(date +%T)"
git push heroku main


# 3. Run Migrations (Using python3 explicitly)
echo "🗄️ Running migrations..."
heroku run python3 manage.py migrate --app $APP_NAME

echo "✅ Deployment Complete!"
heroku open --app $APP_NAME