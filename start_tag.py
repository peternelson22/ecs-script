import os
import boto3
import logging
import json
import sys
import signal
import traceback
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ecs_client = boto3.client("ecs")

def start_services_by_tags(clusters: list[dict]) -> None:
    try:
        for cluster in clusters:
            tag_key = cluster.get('tag_key')
            tag_value = cluster.get('tag_value')
            services = cluster.get('services', {})

            response = ecs_client.list_clusters()
            cluster_arns = response.get('clusterArns', [])

            filtered_clusters = [
                cluster_arn for cluster_arn in cluster_arns
                if cluster_has_all_tags(cluster_arn, tag_key, tag_value)
            ]

            for cluster_arn in filtered_clusters:
                logger.info(f"Checking services in cluster {cluster_arn}")

                cluster_tags_response = ecs_client.list_tags_for_resource(resourceArn=cluster_arn)
                cluster_tags = {tag['key']: tag['value'] for tag in cluster_tags_response.get('tags', {})}
                logger.info(f"Cluster {cluster_arn} tags: {cluster_tags.get(tag_key)}")

                services_arns = ecs_client.list_services(cluster=cluster_arn).get('serviceArns', [])

                for service_arn in services_arns:
                    service_name = service_arn.split('/')[-1]

                    service_tags_response = ecs_client.list_tags_for_resource(resourceArn=service_arn)
                    service_tags = {tag['key']: tag['value'] for tag in service_tags_response.get('tags', {})}
                    logger.info(f"Service {service_name} tags: {service_tags}")

                    for service_tag_value in service_tags.values():
                        if service_tag_value is not None:
                            desired_count = services.get(service_tag_value, 0)

                            ecs_client.update_service(
                                cluster=cluster_arn,
                                service=service_name,
                                desiredCount=desired_count,
                            )
                            logger.info(f"Service {service_name} in cluster {cluster_arn} started (desired count set to {desired_count}).\n")
                        else:
                            logger.warning(f"Tag value {service_tag_value} not found for service {service_name} in cluster {cluster_arn}. Skipping service.\n")

    except ecs_client.exceptions.ClientError as e:
        error_message = e.response.get('Error', {}).get('Message')
        logger.error(f"Error starting services. Message: {error_message}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        traceback.print_exc()

def cluster_has_all_tags(cluster_arn: str, tag_key: str, tag_value: str) -> bool:
    try:
        response = ecs_client.list_tags_for_resource(resourceArn=cluster_arn)
        cluster_tags = {tag['key']: tag['value'] for tag in response.get('tags', {})}

        cluster_has_tags = cluster_tags.get(tag_key) == tag_value

        return cluster_has_tags

    except ecs_client.exceptions.ClientError as e:
        error_message = e.response.get('Error', {}).get('Message')
        logger.error(f"Error checking tags for cluster {cluster_arn}. Message: {error_message}")
        return False

def handle_exit(signum, frame):
    logger.info("Received signal to exit. Exiting gracefully.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

if __name__ == "__main__":
    clusters_json = os.getenv('CLUSTERS', '[]')
    clusters = json.loads(clusters_json)

    start_services_by_tags(clusters)

    print("\nOperation finished.")
