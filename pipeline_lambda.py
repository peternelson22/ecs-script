import boto3

def lambda_handler(event, context):
    # Enter the names of the pipelines
    pipeline_names = ['Pipeline1', 'Pipeline2', 'Pipeline3', 'Pipeline4', 'Pipeline5']

    codepipeline = boto3.client('codepipeline')

    try:
        for pipeline_name in pipeline_names:
            try:
                response = codepipeline.start_pipeline_execution(name=pipeline_name)
                print(f"Pipeline execution started for {pipeline_name}: {response}")
            except codepipeline.exceptions.PipelineNotFoundException as ex:
                print(f"Pipeline {pipeline_name} not found. Skipping...")
            except Exception as ex:
                print(f"Error starting pipeline {pipeline_name}: {ex}")

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
