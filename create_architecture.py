import boto3
import json
# Creating EC2 instance
ec2 = boto3.resource('ec2')

# Creating IAM client
iam = boto3.client('iam')

# IAM role name
role_name = 'ec2_s3_access'
bucket_name = '1919196-s3'
# Check if IAM role already exists
try:
    role = iam.get_role(RoleName=role_name)
    role_arn = role['Role']['Arn']
    print(f"IAM role {role_name} already exists")
except iam.exceptions.NoSuchEntityException:
    # Create IAM role if it does not exist
    assume_role_policy_document = {
        'Version': '2012-10-17',
        'Statement': [
            {
                'Effect': 'Allow',
                'Action': 's3:PutObject',
                'Resource': 'arn:aws:s3::bucket_name*'
            }
        ]
    }

    create_role_response = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(assume_role_policy_document)
    )

    role_arn = create_role_response['Role']['Arn']
    print(f"IAM role {role_name} created")

    # Attach S3 access policy to IAM role
    policy_arn = 'arn:aws:iam::aws:policy/AmazonS3FullAccess'
    iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_arn
    )
    print(f"Attached S3 access policy {policy_arn} to IAM role {role_name}")

# Creating EC2 instance
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
    ],
    IamInstanceProfile={
        'Arn': role_arn
    }
)

print(f"EC2 instance created with IAM role {role_name}")


# Creating S3 bucket

s3 = boto3.resource('s3')
s3.create_bucket(Bucket=bucket_name)

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