# Azure Batch Auto Scale

This python script uses the Azure Batch Python API to implement auto scaling for pools running MPI tasks.  The auto scaling parameters currently provided by Azure Batch (https://docs.microsoft.com/en-us/azure/batch/batch-automatic-scaling) do not expose sufficient information on the multi-instance tasks to implement an auto scaling formula for a pool.  Instead this can be used as a work-around for such cases.

Assumptions:

* Non-MPI tasks require the full node
* Task dependencies are only specified by name (range is not currently supported)

## Running

    usage: scale_pools.py [-h] [-p POOLS] [-m MAX_NODES] [-l LOOP]
                          [-n ACCOUNT_NAME] [-u ACCOUNT_URL] [-k ACCOUNT_KEY]

    optional arguments:
      -h, --help            show this help message and exit
      -p POOLS, --pools POOLS
                            comma separated list of pools (all pools if empty)
      -m MAX_NODES, --max-nodes MAX_NODES
                            maximum number of nodes for a pool
      -l LOOP, --loop LOOP  if non-zero continuously repeating the auto scale
                            sleeping for this number of seconds
      -n ACCOUNT_NAME, --account-name ACCOUNT_NAME
                            the Batch account name
      -u ACCOUNT_URL, --account-url ACCOUNT_URL
                            the Batch account URL
      -k ACCOUNT_KEY, --account-key ACCOUNT_KEY
                            the Batch account key

Ensure your MAX_NODES is not greater than your quota (otherwise if more nodes are requested the pool will not resize and get stuck in a loop returning capacity exceeded)

## Deploying with Docker

Building with docker:

    docker build --tag <DOCKERHUB-USERNAME>/batchautoscale:v1.0.0 .

Push to DockerHub:

    docker push <DOCKERHUB-USERNAME>/batchautoscale:v1.0.0

Running on an Azure Container Instance:

    az container create \
        --resource-group <RESOURCE_GROUP> \
        --location <LOCATION> \
        --name <NAME> \
        --image <DOCKERHUB-USERNAME>/batchautoscale:v1.0.0 \
        --restart-policy Never \
        --command-line 'python /scale_pools.py \
            --account-name <BATCH_ACCOUNT> \
            --account-url <BATCH_URL> \
            --account-key <BATCH_KEY> \
            --loop 60'

