import boto3
import sys

ec2 = boto3.resource('ec2')

def health_check():
    for status in ec2.meta.client.describe_instance_status()['InstanceStatuses']:
        print(status)

def __init__(self):
    self.health_check()
