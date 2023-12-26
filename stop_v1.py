import boto3
import os
import json
import logging
import sys
import signal
import time
import argparse
import traceback
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ecs_client = boto3.client("ecs")

def update_services(cluster_name:str, service_counts: list[str]) -> None:
    for service_name, desired_count in service_counts.items():
        try:
            desired_count = 0  
            ecs_client.update_service(
                cluster=cluster_name,
                service=service_name,
                desiredCount=desired_count,
            )
            logger.info(f"Service {service_name} in cluster {cluster_name} stopped successfully.")
            time.sleep(2)
        except ecs_client.exceptions.ServiceNotFoundException:
            logger.error(f"Service {service_name} not found in cluster {cluster_name}")
        except ecs_client.exceptions.ClientError as e:
            error_message = e.response.get('Error', {}).get('Message')
            logger.error(f"Error stopping service {service_name} in cluster {cluster_name}. Message: {error_message}")
        except Exception as e:
            logger.error(f"Unexpected error stopping service {service_name} in cluster {cluster_name}: {e}")
            traceback.print_exc()

def handle_exit(signum, frame):
    logger.info("Received signal to exit. Exiting gracefully.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

def parse_command_line_args():
    parser = argparse.ArgumentParser(description='Start ECS services with desired count based on groups.')
    parser.add_argument('-c', '--cluster', required=False, help='Name of the ECS cluster')
    parser.add_argument('-s', '--services', nargs='+', required=False, help='List of ECS service names')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_command_line_args()

    clusters = json.loads(os.getenv("CLUSTERS", "[]"))

    for cluster in clusters:
        service_counts = cluster["services"]
        if clusters and not (args.cluster and args.services):
            update_services(cluster["name"], service_counts)
        elif args.cluster and args.services:
            update_services(cluster["name"], service_counts)
        else:
            print("No valid input provided. Please specify cluster and services.")

    print("\n Operation finished")
