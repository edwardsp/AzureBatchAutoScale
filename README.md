



Building with docker:

    docker build --tag paulmedwards/batchautoscale:v1.0.0 .

Push to DockerHub:

    docker push paulmedwards/batchautoscale:v1.0.0

Running on an Azure Container Instance:

    az container create \
        --resource-group <RESOURCE_GROUP> \
        --location <LOCATION> \
        --name <NAME> \
        --image paulmedwards/batchautoscale:v1.0.0 \
        --restart-policy Never \
        --command-line 'python /scale_pools.py \
            --account-name <BATCH_ACCOUNT> \
            --account-url <BATCH_URL> \
            --account-key <BATCH_KEY> \
            --loop 60'

