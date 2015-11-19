#!/usr/bin/python3.4

import os, sys, json, boto3
from pprint import pprint



## 
# Presenting 
# - ami : 
# - ima :
# - ec2 :
# - elb :
# - as  :
# - vpc :
# - subnet : 
# - routes :
# - key-pairs : 
# - security groups  :
# - internet gateway :
##




def print_ec2(  ):
	ec2con = boto3.resource( "ec2" )

	keys = {}
	instance_id_list = []
	instance_states = {}

	instances = ec2con.instances.filter( Filters=[ {'Name': 'instance-state-name', 'Values': ['*']} ])
	
	for instance in instances:
		print( instance.id, instance.instance_type, instance.image_id, instance.state )

		if instance.state['Name'] not in instance_states:
			instance_states[ instance.state['Name'] ] = [];

		instance_states[ instance.state['Name'] ].append( instance.id );

		if( instance.key_name not in keys ):
			kv = ec2con.KeyPair( instance.key_name )
			keys[ instance.key_name ] = kv.key_fingerprint

	
	return instance_states



if __name__ == "__main__":
	print_ec2()