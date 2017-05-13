import boto3
import sys

ec2 = boto3.resource('ec2')

def terminate_instance():
    print "Terminating selected instance(s)"
    for i in range(1,len(sys.argv)):
        ec2.instances.filter(InstanceIds=[str(sys.argv[i])]).terminate()
        print "Instance " + sys.argv[i]+ " terminated successfully"

def __init__(self):
    self.terminate_instance()
