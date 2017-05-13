import boto3
import sys

client = boto3.client('autoscaling')

def create_auto_scaling_group():
    response = client.create_auto_scaling_group(
    AutoScalingGroupName='group1',
    InstanceId=str(sys.argv[1]),
    MinSize=2,
    MaxSize=2,
    )

def __init__(self):
    self.create_auto_scaling_group()
