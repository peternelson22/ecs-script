import os
import json
import boto3
import logging
import sys
import signal
import traceback
from dotenv import load_dotenv
from colorama import Fore, Style

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ecs_client = boto3.client("ecs")

def stop_services_by_tags(tags: list[dict]) -> None:
    try:
        response = ecs_client.list_clusters()
        cluster_arns = response.get('clusterArns', [])

        filtered_clusters = [
            cluster_arn for cluster_arn in cluster_arns
            if cluster_has_any_tags(cluster_arn, tags)
        ]

        if not filtered_clusters:
            logger.info("No clusters found with the specified tags. Exiting.")
            return

        logger.info(f"Clusters to process: {filtered_clusters}")

        services_to_stop = []
        for cluster_arn in filtered_clusters:
            services_arns = ecs_client.list_services(cluster=cluster_arn).get('serviceArns', [])
            services_to_stop.extend(services_arns)

        if not services_to_stop:
            logger.info("No services found in the clusters. Exiting.")
            return

        update_services_batch(filtered_clusters, services_to_stop, desired_count=0)

    except ecs_client.exceptions.ClientError as e:
        error_message = e.response.get('Error', {}).get('Message')
        logger.error(f"Error stopping services. Message: {error_message}")
        traceback.print_exc()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        traceback.print_exc()

def update_services_batch(clusters: list, services: list, desired_count: int) -> None:
    try:
        logger.info(f"Stopping {len(services)} services in {len(clusters)} clusters.")

        for cluster_arn in clusters:
            logger.info(f"Processing cluster: {cluster_arn}")
            services_arns = ecs_client.list_services(cluster=cluster_arn).get('serviceArns', [])

            for service_arn in services_arns:
                service_name = service_arn.split('/')[-1]
                
                if service_arn in services:  
                    try:
                        ecs_client.update_service(
                            cluster=cluster_arn,
                            service=service_name,
                            desiredCount=desired_count,
                        )
                        logger.info(f"{Fore.RED}Service {service_name} in cluster {cluster_arn} stopped (desired count set to {desired_count}).{Style.RESET_ALL}")
                    except ecs_client.exceptions.ServiceNotFoundException:
                        logger.warning(f"{Fore.YELLOW}Service {service_name} not found in cluster {cluster_arn}. Skipping service.{Style.RESET_ALL}")
                else:
                    logger.info(f"Service {service_name} in cluster {cluster_arn} is not in the list of services to be stopped. Skipping.")

        logger.info(f"{Fore.RED}Services stopped successfully.{Style.RESET_ALL}")

    except ecs_client.exceptions.ClientError as e:
        error_message = e.response.get('Error', {}).get('Message')
        logger.error(f"Error updating services. Message: {error_message}")
        traceback.print_exc()

def cluster_has_any_tags(cluster_arn: str, tags: list[dict]) -> bool:
    try:
        response = ecs_client.list_tags_for_resource(resourceArn=cluster_arn)
        cluster_tags = {tag['key']: tag['value'] for tag in response.get('tags', {})}

        return any(cluster_tags.get(tag['key']) == tag['value'] for tag in tags)

    except ecs_client.exceptions.ClientError as e:
        error_message = e.response.get('Error', {}).get('Message')
        logger.error(f"Error checking tags for cluster {cluster_arn}. Message: {error_message}")
        traceback.print_exc()
        return False

def handle_exit(signum, frame):
    logger.info("Received signal to exit. Exiting gracefully.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

if __name__ == "__main__":
    tags_json = os.getenv('STOP_TAGS', '[]')
    tags = json.loads(tags_json)

    stop_services_by_tags(tags)

    print("\nOperation ended!")
