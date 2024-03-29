import boto3
import os
import time
from botocore.exceptions import ClientError

# Creating EC2 and S3 resources
ec2 = boto3.resource('ec2')
s3 = boto3.client('s3')
iam = boto3.client('iam')

bucket_name = '1919196-s3'
role_name = 'EMR_EC2_DefaultRole'  


# Create an S3 bucket
try:
    s3.create_bucket(Bucket=bucket_name)
    print(f'S3 bucket {bucket_name} created.')
except ClientError as e:
    print(e)


# Creating SQS queue and DynamoDB table
cloudformation = boto3.client('cloudformation')
stack_name = 'stack-1919196'

# Creating SQS queue
with open('cf/sqs_template.json', 'r') as f:
    sqs_template_body = f.read()

response = cloudformation.create_stack(
    StackName=f"{stack_name}-sqs",
    TemplateBody=sqs_template_body
)
print(response)


# Creating DynamoDB table
with open('cf/dynamodb_template.json', 'r') as f:
    dynamodb_template_body = f.read()

response = cloudformation.create_stack(
    StackName=f"{stack_name}-dynamodb",
    TemplateBody=dynamodb_template_body
)
print(response)

#wait until the sqs queue is created
waiter = cloudformation.get_waiter('stack_create_complete')
waiter.wait(StackName=f"{stack_name}-sqs")

def get_sqs_arn_by_name(name):
    sqs = boto3.client('sqs')

    # Get the URL of the queue
    queue_url = sqs.get_queue_url(QueueName=name)['QueueUrl']

    # Get the queue's attributes
    attributes = sqs.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=['QueueArn']
    )

    # Extract the ARN from the attributes
    queue_arn = attributes['Attributes']['QueueArn']
    return queue_arn
# Create a bucket notification configuration to send a message to the SQS queue when a file is uploaded to the "transcribe" folder
queue_arn = get_sqs_arn_by_name('1919196queue')
notification_config = {
    'QueueConfigurations': [
        {
            'Id': 'S3ToSQSNotification',
            'QueueArn': queue_arn,
            'Events': [
                's3:ObjectCreated:*'
            ],
            'Filter': {
                'Key': {
                    'FilterRules': [
                        {
                            'Name': 'prefix',
                            # triggering sqs for uploads only under the transcribe object
                            'Value': 'transcribe/'
                        }
                    ]
                }
            }
        }
    ]
}

# Set the bucket notification configuration
try:
    s3.put_bucket_notification_configuration(
        Bucket=bucket_name,
        NotificationConfiguration=notification_config
    )
    print(f'S3 bucket {bucket_name} notification configuration set.')
except ClientError as e:
    print(e)


# Check if IAM role already exists
try:
    role = iam.get_role(RoleName=role_name)
    role_arn = role['Role']['Arn']
except ClientError as e:
    print(e)

# Define user data to run the configure_instance.sh script upon instance launch
user_data = '''#!/bin/bash
yum update -y
aws s3 sync s3://{0}/setup /home/ec2-user/setup
sudo chmod -R 777 /home/ec2-user/setup
/home/ec2-user/setup/configure_instance.sh
'''.format(bucket_name)

# Creating EC2 instance
instances = ec2.create_instances(
        ImageId="ami-06e46074ae430fba6",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName="connect_ec2",
        UserData=user_data,
        IamInstanceProfile={'Arn': 'arn:aws:iam::664716271474:instance-profile/EMR_EC2_DefaultRole'},
        TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': '1919196-ec2'
                },
            ]
        },
    ],
)


