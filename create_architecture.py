import boto3


# Creating EC2 instance
ec2 = boto3.resource('ec2')

instances = ec2.create_instances(
        ImageId="ami-06e46074ae430fba6",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName="connect_ec2",
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
s3.create_bucket(Bucket='1919196-s3')

# Creating SQS queue and DynamoDB table
cloudformation = boto3.client('cloudformation')
stack_name = 'stack-1919196'

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