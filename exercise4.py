from operator import itemgetter

import boto3

ecr_client = boto3.client('ecr')

ecrs = ecr_client.describe_repositories()

for repo in ecrs['repositories']:
    print(f'Name: {repo["repositoryName"]}')


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
