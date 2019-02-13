import re
import boto3
import csv
from botocore.exceptions import ClientError
ec2 = boto3.client('ec2')
regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]

def get_snapshots(e):
    return e.describe_snapshots(OwnerIds=['self'])['Snapshots']

def volume_exists(e , volume_id):
    if volume_id=='':
        return ''
    try:
        e.describe_volumes(VolumeIds=[volume_id])
        return True
    except ClientError:
        return False

def instance_exists(e, instance_id):
    if not instance_id: return ''
    try:
        e.describe_instances(InstanceIds=[instance_id])
        return True
    except ClientError:
        return False

def image_exists(e, image_id):
    if not image_id: return ''
    try:
        requestObj = e.describe_images(ImageIds=[image_id,])
        if not requestObj["Images"]:
            return False
        return True
    except ClientError:
        return False

def parse_description(description):
    regex = r"^Created by CreateImage\((.*?)\) for (.*?) "
    matches = re.finditer(regex, description, re.MULTILINE)
    for matchNum, match in enumerate(matches):
        return match.groups()
    return '', ''

def main():
    with open('allregionreport.csv', 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'region',
            'snapshot id',
            'description',
            'started',
            'size',
            'volume',
            'volume exists',
            'instance',
            'instance exists',
            'ami',
            'ami exists'])
        for region in regions:
            ec2 = boto3.client('ec2', region_name=region)
            for snap in get_snapshots(ec2):
                instance_id, image_id = parse_description(snap['Description'])
                writer.writerow([
                    region,
                    snap['SnapshotId'],
                    snap['Description'],
                    snap['StartTime'],
                    str(snap['VolumeSize']),
                    snap['VolumeId'],
                    str(volume_exists(ec2, snap['VolumeId'])),
                    instance_id,
                    str(instance_exists(ec2, instance_id)),
                    image_id,
                    str(image_exists(ec2,image_id)),
                ])

if __name__ == '__main__':
    main()
