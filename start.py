import boto3
import json
import logging
import os
import time
from dotenv import load_dotenv
from typing import Dict

load_dotenv()  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ecs_client = boto3.client('ecs')

def start_ecs_service(cluster_name: str, service_name: str, desired_counts: Dict[str, int]) -> None:
    """
    Start ECS services with the desired number of tasks.

    Parameters:
    - cluster_name (str): Name of the ECS cluster.
    - service_name (str): ECS service name.
    - desired_count Dict[str, int]: Desired count for ECS services.

    Returns:
    - None
    """
    try:
        desired_count = desired_counts.get(service_name, 1)
        ecs_client.update_service(
            cluster=cluster_name,
            service=service_name,
            desiredCount=desired_count
        )

        logger.info(f"Service {service_name} in cluster {cluster_name} started successfully")
        time.sleep(1)
    except ecs_client.exceptions.ServiceNotFoundException:
        logger.error(f"Service not found in cluster {cluster_name}")
    except ecs_client.exceptions.ClientError as e:
        error_message = e.response.get('Error', {}).get('Message')
        logger.error(f"Error starting services in cluster {cluster_name}. Message: {error_message}")
    except Exception as e:
        logger.error(f"Unexpected error in cluster {cluster_name}: {e}")

if __name__ == "__main__":
    i = 1
    while True:
        cluster_name = os.environ.get(f'CLUSTER_{i}')
        if not cluster_name:
            break
        service_list = json.loads(os.environ.get(f'SERVICES_CLUSTER_{i}', '[]'))
        desired_counts = json.loads(os.environ.get(f'DESIRED_COUNTS_CLUSTER_{i}', '{}'))

        for service_name in service_list:
            start_ecs_service(cluster_name, service_name, desired_counts)

        i += 1
