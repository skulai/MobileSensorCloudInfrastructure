import boto3
import sys
import time

ec2 = boto3.resource('ec2')
client = boto3.client('ec2')

def create_instance():
    instance = ec2.create_instances(
        ImageId='ami-ceeda6ae',
        MinCount=1,
        MaxCount=1,
        KeyName='local',
        SecurityGroups=['openstackaccess'],
        DryRun = False,
        InstanceType='t1.micro'
        )

    print "Instance creation in progress! Please wait for a while! \n"
    instance[0].wait_until_running()
    instance[0].reload()
    print "\nInstance created successfully, below are the details \n"

    instancedict = {
        'id': instance[0].id,
        'ip_address': instance[0].public_ip_address,
        'dns': instance[0].public_dns_name,
        'instance_type': instance[0].instance_type,
        'status': instance[0].state['Name']
    }

    for i in instancedict:
        print i, str(instancedict[i]) + "\n"

    return instancedict

#create_instance()

def __init__(self):
    pass

# print "Please ssh to the instance using below command: \n"
# print "ssh -i "+instance[0].key_name + ".pem " + "
