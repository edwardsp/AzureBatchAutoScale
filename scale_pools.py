#!/usr/bin/python

import argparse
import json
import os
import time

import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batchauth
import azure.batch.models as batchmodels

from collections import namedtuple

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pools', help='comma separated list of pools (all pools if empty)')
    parser.add_argument('-m', '--max-nodes', help='maximum number of nodes for a pool', default=1000, type=int)
    parser.add_argument('-l', '--loop', help='if non-zero continuously repeating the auto scale sleeping for this number of seconds', default=0, type=int)
    parser.add_argument('-n', '--account-name', help='the Batch account name')
    parser.add_argument('-u', '--account-url', help='the Batch account URL')
    parser.add_argument('-k', '--account-key', help='the Batch account key')
    args = parser.parse_args()

    BATCH_ACCOUNT_NAME = args.account_name
    BATCH_ACCOUNT_URL = args.account_url
    BATCH_ACCOUNT_KEY = args.account_key
    POOL_MAX_NODES = args.max_nodes
    LOOP = args.loop
    POOLS = args.pools

    print("account name: ", BATCH_ACCOUNT_NAME)
    print("account URL: ", BATCH_ACCOUNT_URL)
    print("account key: ", BATCH_ACCOUNT_KEY)

    credentials = batchauth.SharedKeyCredentials(BATCH_ACCOUNT_NAME, BATCH_ACCOUNT_KEY)
    batch_client = batch.BatchServiceClient(credentials, base_url=BATCH_ACCOUNT_URL)

    BatchTask = namedtuple("BatchTask", "pool_name job_name task_name state nodes deps")

    # Get pools here
    if POOLS:
        pool_list = POOLS.split(',')
    else:
        pool_list = [ pool.id for pool in batch_client.pool.list() ]

    while True:
        output = []

        for pool_name in pool_list:
            task_list = []

            # get all the active jobs
            # https://docs.microsoft.com/en-us/rest/api/batchservice/job/list
            job_filter_str = "(state eq 'active') and (executionInfo/poolId eq '{}')"
            for job in batch_client.job.list(batchmodels.JobListOptions(job_filter_str.format(pool_name))):                            
                job_name = job.id
                pool_name = job.pool_info.pool_id
                job_uses_dependencies = job.uses_task_dependencies
                
                # https://docs.microsoft.com/en-us/rest/api/batchservice/task/list
                all_tasks = {}
                for task in batch_client.task.list(job_name, batchmodels.TaskListOptions("(state eq 'active') or (state eq 'running')")):
                    all_tasks[task.id] = task
                
                for task_id, task in all_tasks.items():
                    # check the number of nodes required
                    num_nodes = 1
                    if task.multi_instance_settings:
                        num_nodes = task.multi_instance_settings.number_of_instances
                    
                    # gather dependencies that have not completed
                    deps = []
                    if task.depends_on:
                        for dep in task.depends_on.task_ids:
                            if all_tasks[dep].state != batchmodels.TaskState.completed:
                                deps.append(dep)
                        
                    # now add to correct list
                    state = "null"
                    if task.state == batchmodels.TaskState.running:
                        state = "running"
                    elif task.state == batchmodels.TaskState.active:
                        if len(deps) > 0:
                            state = "waiting"
                        else:
                            state = "ready"

                    # create batch task       
                    if state != "null":
                        task_list.append(BatchTask(pool_name, job_name, task_id, state, num_nodes, deps))

            nrunning = sum([t.nodes for t in task_list if t.state == "running" and t.pool_name == pool_name])
            nready = sum([t.nodes for t in task_list if t.state == "ready" and t.pool_name == pool_name])
            nwaiting = sum([t.nodes for t in task_list if t.state == "waiting" and t.pool_name == pool_name])
            
            pool = batch_client.pool.get(pool_name)
            pool_current_nodes = pool.current_dedicated_nodes

            required_nodes = nrunning + nready
            new_target = min(POOL_MAX_NODES, required_nodes)

            resized = False
            if new_target != pool_current_nodes and pool.allocation_state == batchmodels.AllocationState.steady:
                resized = True
                batch_client.pool.resize(pool_name, batchmodels.PoolResizeParameter(target_dedicated_nodes=new_target))

            output.append({
                pool_name: {
                    "running": nrunning,
                    "ready": nready,
                    "waiting": nwaiting,
                    "current": pool_current_nodes,
                    "required": required_nodes,
                    "max": POOL_MAX_NODES,
                    "target": new_target,
                    "resized": resized
                }
            })

        print(json.dumps(output))
        if LOOP == 0:
            break
        time.sleep(LOOP)
