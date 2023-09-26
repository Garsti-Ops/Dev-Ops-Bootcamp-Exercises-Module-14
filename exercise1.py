import boto3

client = boto3.client('ec2')

response = client.describe_subnets(
    Filters=[{
        'Name': 'availabilityZone',
        'Values': ['eu-central-1']
    }]
)

for subnet in response['Subnets']:
    print(subnet['SubnetId'])