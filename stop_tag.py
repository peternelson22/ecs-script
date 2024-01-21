import os
import json
import boto3
import sys
import logging
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

        for cluster_arn in filtered_clusters:
            logger.info(f"Checking services in cluster {cluster_arn}")

            services_arns = ecs_client.list_services(cluster=cluster_arn).get('serviceArns', [])

            for service_arn in services_arns:
                service_name = service_arn.split('/')[-1]

                ecs_client.update_service(
                    cluster=cluster_arn,
                    service=service_name,
                    desiredCount=0,
                )
                logger.info(f"{Fore.RED}Service {service_name} in cluster {cluster_arn} stopped (desired count set to 0).{Style.RESET_ALL}")

    except ecs_client.exceptions.ClientError as e:
        error_message = e.response.get('Error', {}).get('Message')
        logger.error(f"Error stopping services. Message: {error_message}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        traceback.print_exc()


def cluster_has_any_tags(cluster_arn: str, tags: list[dict]) -> bool:
    try:
        response = ecs_client.list_tags_for_resource(resourceArn=cluster_arn)
        cluster_tags = {tag['key']: tag['value'] for tag in response.get('tags', {})}

        return any(cluster_tags.get(tag['key']) == tag['value'] for tag in tags)

    except ecs_client.exceptions.ClientError as e:
        error_message = e.response.get('Error', {}).get('Message')
        logger.error(f"Error checking tags for cluster {cluster_arn}. Message: {error_message}")
        return False

def handle_exit(signum, frame):
    logger.info("Received signal to exit. Exiting gracefully.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

if __name__ == "__main__":
    tags_json = os.getenv('STOP_TAGS', '[]')
    tags = json.loads(tags_json)

    stop_services_by_tags(tags)

    print("\nOperation ended! 🙌")
