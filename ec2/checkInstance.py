import boto3
import sys

ec2 = boto3.resource('ec2')

def check_instance():
    print "Currently running instances are as below"
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        print instance.id, instance.instance_type, instance.public_dns_name, instance.public_ip_address

check_instance()

def __init__(self):
    self.check_instance()
