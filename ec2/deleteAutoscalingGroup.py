import boto3

client = boto3.client('autoscaling')

def delete_auto_scaling_group():
    response1 = client.delete_auto_scaling_group(
    AutoScalingGroupName='group1',
    ForceDelete=True
    )

    response2 = client.delete_launch_configuration(
    LaunchConfigurationName='group1'
    )

def __init__(self):
    self.delete_auto_scaling_group()
