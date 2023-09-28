import time
from operator import itemgetter

import boto3
import os

import paramiko
import requests

ecr_client = boto3.client('ecr')

ecrs = ecr_client.describe_repositories()

images = ecr_client.describe_images(
    repositoryName=ecrs['repositories'][0]['repositoryName']
)

image_tags = []

for image in images['imageDetails']:
    image_tags.append({
        'tag': image['imageTags'],
        'pushed_at': image['imagePushedAt']
    })

images_sorted = sorted(image_tags, key=itemgetter("pushed_at"), reverse=True)
for image in images_sorted:
    print(image)

ssh_host = os.environ['EC2_SERVER']
ssh_user = os.environ['EC2_USER']
ssh_private_key = os.environ['SSH_KEY_FILE']

docker_registry = os.environ['ECR_REGISTRY']
docker_user = os.environ['DOCKER_USER']
docker_pwd = os.environ['DOCKER_PWD']
docker_image = os.environ['DOCKER_IMAGE'] # version is selected by user in Jenkins
container_port = os.environ['CONTAINER_PORT']
host_port = os.environ['HOST_PORT']

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=ssh_host, username=ssh_user, key_filename=ssh_private_key)

stdin, stdout, stderr = ssh.exec_command(f"echo {docker_pwd} | docker login {docker_registry} --username {docker_user} --password-stdin")
print(stdout.readlines())
stdin, stdout, stderr = ssh.exec_command(f"docker run -p {host_port}:{container_port} -d {docker_image}")
print(stdout.readlines())

ssh_host = os.environ['EC2_SERVER']
host_port = os.environ['HOST_PORT']

# Validate the application started successfully
try:
    # give the app some time to start up
    time.sleep(15)

    response = requests.get(f"http://{ssh_host}:{host_port}")
    if response.status_code == 200:
        print('Application is running successfully!')
    else:
        print('Application deployment was not successful')
except Exception as ex:
    print(f'Connection error happened: {ex}')
    print('Application not accessible at all')
