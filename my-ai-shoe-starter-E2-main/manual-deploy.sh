### VARIABLES TO CHANGE - START
PROJECT_ID=egarcia154techx25
SERVICE_NAME=my-ai-shoe-starter-e2
### VARIABLES TO CHANGE - END

# ----------- Manual Deployment ------------ #
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}

if [ $? != 0 ]; then
    echo "'gcloud builds' failed!"
    exit 1
fi

gcloud run deploy ${SERVICE_NAME} \
    --image gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest \
    --region us-central1 \
    --allow-unauthenticated

if [ $? != 0 ]; then
    echo "'gcloud run deploy' failed!"
fi
