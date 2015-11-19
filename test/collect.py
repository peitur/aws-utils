
import sys,os
import boto3

from pprint import pprint


AUTOSTART = False
AUTOSTOP = False

## Our main "part"
if( __name__ == "__main__" ):
	ec2con = boto3.resource("ec2")

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


		for interface in instance.network_interfaces_attribute:
			print( "VPC: %(vpcid)s" % { "vpcid":interface['VpcId'] } )

	print("#####################################################################")
	print("Found states:" )
	pprint( instance_states )


	if 'stopped' in instance_states and len( instance_states['stopped'] ) > 0:
		client = boto3.client("ec2")
		print("Can start nodes: %(s)s" % { "s": ",".join( instance_states['stopped'] ) } )
		if AUTOSTART: 
			start_state = client.start_instances( InstanceIds=instance_states['stopped'] )

	elif 'running' in instance_states and len( instance_states['running'] ) > 0:
		client = boto3.client("ec2")
		print("Can stop nodes: %(s)s" % { "s": ",".join( instance_states['running'] ) } )
		if AUTOSTOP: 
			stop_state = client.stop_instances( InstanceIds=instance_states['running'] )

	else:
		print("No actions taken on any insatnces")

	print("#########################")
	if( len( keys.keys() ) > 1 ):
		print("WARN: More then one key-pair used, %(n)s" % {"n": len( keys.keys() ) })

	if( len( keys.keys() ) > 0 ):
		pprint( keys )
	print("#####################################################################")


	defaultvpc = boto3.client("ec2").describe_vpcs()['Vpcs'][0]['VpcId'];
	for vpc in ec2con.Vpc( defaultvpc ).security_groups.all():
		pprint( vpc )

	