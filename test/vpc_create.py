
import sys,os
import boto3

from pprint import pprint









def print_vpcs( vpclist ):
	for v in vpclist:
		print( "VPC: ID: %(id)-16s NW: %(nw)-34s State: %(state)-4s" % { 'id': v['VpcId'],'nw': v['CidrBlock'], 'state': v['State'] }  )


def print_secgroups( sglist ):
	for sg in sglist:
		print("SEG: ID: %(id)-16s Name: %(name)-32s VPC: %(vpc)-16s" % { 'id': sg['GroupId'], 'name': sg['GroupName'],  'vpc': sg['VpcId'] } )
		for ipp in sg['IpPermissions']:
			if 'FromPort' in ipp:
				iprange = []
				for ir in ipp['IpRanges']:
					iprange.append( ir['CidrIp'])

				print("SEC: ... %(proto)-5s : %(fport)-8d => %(tport)-32d Ranges: %(range)s" % { 'proto': ipp['IpProtocol'], 'fport': ipp['FromPort'], 'tport': ipp['ToPort'], 'range': ",".join( iprange ) } )
			else:
				pprint( ipp )


if __name__ == "__main__":

	vpc_cidr = "172.32.0.0/16"
	vpc_name = "Tester1"
	vpc_id = None

	security_group = {
		'name':'sg_test1',
		'descr': 'testing basics ',
	}

	internet_gateway = {

	}

	subnet_list = [
		{
			'name':'tester1_subet1',
			'cidr':"172.32.10.0/24"
		},
		{
			'name':'tester1_subet2',
			'cidr':"172.32.11.0/24"
		}

	]






	print("======== Current Network Info ========")
	client = boto3.client("ec2")

	vpcdata = client.describe_vpcs()
	print_vpcs( vpcdata['Vpcs'] )
	
	sgdata = client.describe_security_groups( )
	print_secgroups( sgdata['SecurityGroups'] )

	task_num = 0

	print("======== Starting creation ========")
	task_num += 1
	print("%(tn)d. Creating new VPC: '%(cidr)s' as '%(name)s'" % {'tn': task_num, 'cidr': vpc_cidr, 'name': vpc_name } )
	## Create VPC
	## Attach Tag with name
	vpc_id = "vpc-123123"

	if not vpc_id:
		print("ERROR: Could not create VPC, aborting")
		sys.exit()

	task_num += 1
	print("%(tn)d. Getting the new VPCs (%(vpc)s) routing table" % {'tn': task_num, 'vpc': vpc_id} )

	task_num += 1
	print("%(tn)d. Create Security Group %(name)s for VPC %(vpc)s" % { 'tn': task_num, 'name': security_group['name'], 'vpc': vpc_id } )
	## Create
	## Attach Tag with name

	task_num += 1
	print("%(tn)d. Create Internet Gateway " % { 'tn': task_num } )
	## Create 
	## Attach Tag with name

	task_num += 1
	stask_num = 0
	print("%(tn)d. Create %(ln)s subnets" % { 'tn': task_num, 'ln': len( subnet_list ) } )
	for net in subnet_list:
		stask_num += 1
		print("%(tn)d.%(stn)d. Creating %(cidr)s as %(name)s" % { 'tn': task_num, 'stn': stask_num,'cidr': net['cidr'],'name': net['name'] } )

		## Create 
		## Attach Tag with name

	




