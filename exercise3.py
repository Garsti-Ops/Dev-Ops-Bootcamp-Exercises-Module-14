import boto3
import paramiko
import time
import requests
import schedule

ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')

# Create Instance
instance = ec2_resource.create_instance(
    ImageId="ami-01342111f883d5e4e",
    InstanceType="t2.micro",
    MinCount=1,
    MaxCount=1,
    KeyName="docker-server"
)

# Get Public IPv4
instance.wait_until_running()
public_ip = instance[0].wait_until_running()

# SSH and install docker
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

private_rsa_key = paramiko.RSAKey.from_private_key_file('/home/cheider/.ssh/docker-server.pem')
ssh_client.connect(hostname=public_ip, username="ec2-user", pkey=private_rsa_key)
stdin, stdout, stderr = ssh_client.exec_command('''
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
''')
time.sleep(20)

stdin, stdout, stderr = ssh_client.exec_command('sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin')
time.sleep(20)

stdin, stdout, stderr = ssh_client.exec_command('docker run --name some-nginx -d -p 8080:80 nginx-my-dude')
ssh_client.close()

# Create new Security Group
sg_list = ec2_client.describe_security_groups(
    GroupNames=['default']
)

# Add ingress Rule
ig_rule = ec2_client.authorize_security_group_ingress(
    CidrIp="0.0.0.0/0",
    FromPort=8080,
    GroupId=sg_list['SecurityGroups'][0]['GroupId'],
    ToPort=8080
)



def check_server_status(public_ip):
    response = requests.get(public_ip)

    if response.status_code != 200:
        retrys = 0

        while retrys < 5:
            response = requests.get(public_ip)

            if response.status_code == 200:
                return
            else:
                retrys += 1
                time.sleep(10)


        stdin, stdout, stderr = ssh_client.exec_command('docker restart nginx-my-dude')

schedule.every(10).minutes.do(check_server_status(public_ip))