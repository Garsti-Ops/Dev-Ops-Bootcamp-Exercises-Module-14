from operator import itemgetter

import boto3

client = boto3.client('iam')

response = client.list_users()

# Print name, last active and id and name of most active user
sorted_users = sorted(response['Users'], key=itemgetter('PasswordLastUsed'), reverse=True)
print(f'Most active User-Id: {sorted_users[0]["UserId"]}, Username: {sorted_users[0]["UserName"]}\n\n')

for user in response['Users']:
    print(f'Username: {user["UserName"]}, last active: {user["PasswordLastUsed"]}')