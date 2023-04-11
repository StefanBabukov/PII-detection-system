import boto3

# Creating EC2 instance
ec2 = boto3.resource('ec2')

bucket_name = '1919196-s3'
stack_name = 'stack-1919196'

# User data script to download and execute files
user_data = f'''#!/bin/bash
aws s3 cp upload_to_s3.py /home/ec2-user/upload_to_s3.py
chmod +x /home/ec2-user/upload_to_s3.py
aws s3 cp configure_instance.sh /home/ec2-user/configure_instance.sh
aws s3 cp audio_files /home/ec2-user/audio_files
chmod +x /home/ec2-user/configure_instance.sh
/home/ec2-user/configure_instance.sh
'''

instances = ec2.create_instances(
        ImageId="ami-06e46074ae430fba6",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName="connect_ec2",
        UserData=user_data,  
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
    ]
    )

# Creating S3 bucket
s3 = boto3.resource('s3')
s3.create_bucket(Bucket=bucket_name)

# Creating SQS queue and DynamoDB table
cloudformation = boto3.client('cloudformation')

# Creating SQS queue
with open('sqs_template.json', 'r') as f:
    sqs_template_body = f.read()

response = cloudformation.create_stack(
    StackName=f"{stack_name}-sqs",
    TemplateBody=sqs_template_body
)
print(response)

# Creating DynamoDB table
with open('dynamodb_template.json', 'r') as f:
    dynamodb_template_body = f.read()

response = cloudformation.create_stack(
    StackName=f"{stack_name}-dynamodb",
    TemplateBody=dynamodb_template_body
)
print(response)