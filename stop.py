import boto3
import os
import argparse
import logging
import json
import time
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv() 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ecs_client = boto3.client('ecs')

def stop_all_services(clusters_services: Dict[str, List[str]]) -> None:
    """
    Stop all specified ECS services in the given clusters.

    Parameters:
    - clusters_services (Dict[str, List[str]]): Dictionary with clusters and their corresponding services.

    Returns:
    - None
    """
    for cluster_name, service_names in clusters_services.items():
        for service_name in service_names:
            try:
                ecs_client.update_service(
                    cluster=cluster_name,
                    service=service_name,
                    desiredCount=0  
                )

                logger.info(f"Service {service_name} in cluster {cluster_name} stopped successfully.")
                time.sleep(1)
            except ecs_client.exceptions.ServiceNotFoundException:
                logger.error(f"Service {service_name} not found in cluster {cluster_name}")
            except ecs_client.exceptions.ClientError as e:
                error_message = e.response.get('Error', {}).get('Message')
                logger.error(f"Error stopping service {service_name} in cluster {cluster_name}. Message: {error_message}")
            except Exception as e:
                logger.error(f"Unexpected error stopping service {service_name} in cluster {cluster_name}: {e}")

def parse_command_line_args():
    parser = argparse.ArgumentParser(description='Start ECS services with desired count based on groups.')
    parser.add_argument('-c', '--cluster', required=False, help='Name of the ECS cluster')
    parser.add_argument('-s', '--services', nargs='+', required=False, help='List of ECS service names')

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_command_line_args()

    clusters_services = {}
    i = 1
    while True:
        cluster_name = os.environ.get(f'STOP_CLUSTER_{i}')
        if not cluster_name:
            break  
        service_list = json.loads(os.environ.get(f'STOP_SERVICES_{i}', '[]'))
        clusters_services[cluster_name] = service_list
        i += 1

    if clusters_services and not (args.cluster and args.services):
        stop_all_services(clusters_services)
    elif args.cluster and args.services:
        clusters_services = {args.cluster: args.services}
        stop_all_services(clusters_services)
    else:
        print("No valid input provided. Please specify cluster and services.")


