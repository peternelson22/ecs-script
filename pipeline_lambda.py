import boto3

def lambda_handler(event, context):
    # define the tag key and value to identify pipelines
    tag_key = 'Env'
    tag_value = 'prod'

    codepipeline = boto3.client('codepipeline')

    try:
        response = codepipeline.list_pipelines()
        pipelines = response['pipelines']

        for pipeline in pipelines:
            pipeline_name = pipeline['name']

            try:
                response_tags = codepipeline.list_tags_for_resource(resourceArn=f'arn:aws:codepipeline:us-east-1:507698722484:{pipeline_name}')

                for tag in response_tags['tags']:
                    if tag['key'] == tag_key and tag['value'] == tag_value:
                        response_execution = codepipeline.start_pipeline_execution(name=pipeline_name)
                        print(f"Pipeline execution started for {pipeline_name}: {response_execution}")
            except codepipeline.exceptions.PipelineNotFoundException:
                print(f"Pipeline '{pipeline_name}' not found. Skipping.")
            except Exception as e:
                print(f"Error processing pipeline '{pipeline_name}': {e}")

        return {
            'statusCode': 200,
            'body': "Pipeline executions started successfully."
        }

    except Exception as e:
        print(f"Error starting pipeline executions: {e}")
        return {
            'statusCode': 500,
            'body': f"Error starting pipeline executions: {e}"
        }

