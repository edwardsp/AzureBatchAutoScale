



    docker build --tag paulmedwards/batchautoscale:v1.0.0 .

    docker push paulmedwards/batchautoscale:v1.0.0

    az container create \
        --resource-group BatchAutoScale \
        --location eastus \
        --name batchautoscale \
        --image paulmedwards/batchautoscale:v1.0.0 \
        --restart-policy Never \
        --command-line 'python /scale_pools.py \
            --account-name BATCH_ACCOUNT \
            --account-url BATCH_URL \
            --account-key BATCH_KEY \
            --loop 60'

