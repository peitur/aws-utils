#!/usr/bin/python3.4

import sys, os, json, yaml, getopt, re
import paramiko

from pprint import pprint

AVG_FILE="/proc/loadavg" 
UPTIME_FILE="/proc/uptime"
MEMINFO_FILE="/proc/meminfo"
FORMATS = ['text','json','yaml']


def load_sitefile( filename, debug = False ):
	
	default_pkey = None
	default_user = None
	result = []

	try:
		fd = open( filename, "r" )
		for line in fd:

			if re.match( r"^\s*#", line ): break

			## format : host  user   pkey
			lline = line.split()
			if   lline[0] == 'DEFAULT_USER': default_user = lline[1]
			elif lline[0] == 'DEFAULT_PKEY': default_pkey = lline[1]
			else:

				user = default_user
				pkeyfile = default_pkey
				if len( lline ) > 1 and lline[1] : user = lline[1]
				if len( lline ) > 2 and lline[2] : pkeyfile = lline[2]

				result.append( { 'host': lline[0], 'user': user, 'pkeyfile': pkeyfile } )

		fd.close()

	except Exception as error:
		raise

	return result

def conenct( host, user, pkeyfile, **opt ):

	port = "22"
	debug = False 

	if "debug" in opt : debug = opt['debug']
	if "port" in opt : port = opt['port']


	if not os.path.exists( pkeyfile ):
		raise RuntimeError( "ERROR: No private key file %(pkey)s" % { 'pkey': pkeyfile } )

	try:
		pkeyref = paramiko.RSAKey.from_private_key_file( pkeyfile )

		client = paramiko.SSHClient()
		client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
		if debug: print( "DEBUG: Connecting to %(host)s with %(user)s using %(pkey)s" % { 'host': host,'user': user, 'pkey': pkeyfile} )

		ret =  client.connect( hostname=host, username=user, key_filename=pkeyfile, timeout=10 )
		
		return client

	except Exception as error:
		pprint( error )
		raise


def close( connection ):
	if connection: connection.close()


def loadavg( client, debug = False ):
	
	command =  "/usr/bin/cat "+AVG_FILE	
	stdin , stdout, stderr = client.exec_command( command )
	output_std = stdout.read().decode( "ascii").strip().split()
	output_err = stderr.read().decode( "ascii").strip().split()

	return {  '1min': output_std[0],'5min': output_std[1],'15min': output_std[2],'queue': output_std[3], 'lastpid': output_std[4] } 


def uptime( client, debug = False ):
	
	command =  "/usr/bin/cat "+UPTIME_FILE
	stdin , stdout, stderr = client.exec_command( command )
	output_std = stdout.read().decode( "ascii").strip().split()
	output_err = stderr.read().decode( "ascii").strip().split()

	return {  'system': output_std[0],'idle': output_std[1] } 


def meminfo( client, debug = False ):

	command =  "/usr/bin/cat "+MEMINFO_FILE
	stdin , stdout, stderr = client.exec_command( command )


	lines = stdout.readlines()
	output_std = {}
	for line in lines:
		llist = line.strip().split()
		if llist[0] == 'MemTotal:': output_std['memtotal'] = llist[1]
		if llist[0] == 'MemFree:': output_std['memfree'] = llist[1]
		if llist[0] == 'MemAvailable:': output_std['memavailable'] = llist[1]
		if llist[0] == 'Buffers:': output_std['buffers'] = llist[1]
		if llist[0] == 'Cached:': output_std['cached'] = llist[1]
		if llist[0] == 'SwapCached:': output_std['swapcached'] = llist[1]
		if llist[0] == 'VmallocTotal:': output_std['vmalloctotal'] = llist[1]
		if llist[0] == 'VmallocUsed:': output_std['vmallocused'] = llist[1]
		if llist[0] == 'SwapTotal:': output_std['swaptotal'] = llist[1]
		if llist[0] == 'SwapFree:': output_std['swapfree'] = llist[1]
		if llist[0] == 'Shmem:': output_std['shmem'] = llist[1]

	output_err = stderr.read().decode( "ascii").strip().split()

	return output_std




def print_values( lhash = {} ):

	print("#######################################")
	print("host.name=%(host)s" % { 'host': lhash['hostname'] } )
	del( lhash['hostname'] )

	for ka in lhash:
		for kb in lhash[ka]:
			print("%(a)s.%(b)s=%(val)s" % { 'a': ka,'b': kb, 'val': lhash[ka][kb] } )
	print("#######################################")



def print_help( ):
	print("--help\t\t\t\tThis help")	
	print("-d|--debug\t\t\tToggle debugging")
	print("-u|--user <user>\t\tUsername")
	print("-p|--pkey <pkey>\t\tPublic key file")
	print("-h|--host <host>\t\tHostname")
	print("-s|--site <sitefile>\t\tSitefile")
	print("-F|--format <frm>\t\tOutputformat [text|json|yaml]")
	print("-P|--port <port>\t\tSSH port to use, default 22")
	print("")
	print("Exmaple:")
	print("#########################################")
	print("ssh_health.py --user ec2-user --host 54.84.46.123 --pkey /home/vagrant/.ssh/aws_test.pem ")
	print("ssh_health.py --site sitefile.txt ")
	print("#########################################")
	print("Site file format:")
	print("<host> <user> <pkeyfile>")
	print("If DEFAULT_USER and DEFAULT_PKEY is defined in file, only host is needed, one per line.")
	print("")
	print("Example:")
	print("#########################################")
	print("DEFAULT_PKEY /home/vagrant/.ssh/aws_test.pem")
	print("DEFAULT_USER vagrant")
	print("54.84.46.125")
	print("54.84.46.123 ec2-user /home/vagrant/.ssh/aws_test2.pem")
	print("54.84.46.123 ec2-user /home/vagrant/.ssh/aws_test1.pem")
	print("54.84.46.124 ec2-user")
	print("#########################################")
	print("")



########################################
if __name__ == "__main__":


	script = sys.argv.pop(0)

	try:
		optlist, args = getopt.getopt( sys.argv , "ds:h:u:p:F:P:", ['help','debug','site=','port=','user=','pkey=','host=','format='])
	except getopt.GetoptError as err:
		print("Options: %(error)s" % { 'error': err.__str__() } )
		sys.exit(1)

	debug = False
	user = None
	port = "22"
	pkeyfile = None
	host = None
	sitefile = None
	format = 'text'

	for opt, arg in optlist:
		if( opt   in ("-d","--debug" ) ): debug = True
		elif( opt in ("-u","--user" ) ): user = arg
		elif( opt in ("-p","--pkey" ) ): pkeyfile = arg
		elif( opt in ("-h","--host" ) ): host = arg
		elif( opt in ("-s","--site" ) ): sitefile = arg
		elif( opt in ("-F","--format" ) ): format = arg
		elif( opt in ("-P","--port" ) ): port = arg
		elif( opt in ("--help" ) ): 
			print_help()
			sys.exit(0)

	if format not in FORMATS:
		print("Unsupported output format %(f)s" % { 'f':format } )
		sys.exit(0)

	conlist = []
	if sitefile:
		conlist = load_sitefile( sitefile, debug )

	if host and pkeyfile and user:
		conlist.append( { "host": host, "pkeyfile": pkeyfile, "user": user } )

	prep=""
	for hdata in conlist:
		try:
			if debug: print("Connecting to %(h)s" % {'h': hdata['host'] } )
			con = conenct( hdata['host'], hdata['user'], hdata['pkeyfile'], debug=debug, port=port )

			data = { 
				prep+"hostname": hdata['host'],
				prep+"loadavg": loadavg( con, debug ),
				prep+"uptime": uptime( con, debug ),
				prep+"meminfo": meminfo( con, debug )
			}


			if debug: 
				print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
				pprint( data )
				print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

			if format in FORMATS and format =='text':
				print_values( data )
			elif format in FORMATS and format =='json':
				print( json.dumps( data ) )
			elif format in FORMATS and format =='yaml':
				print( yaml.dump( data, explicit_start=True, default_flow_style=False ) )

			close( con )

		except Exception as error:
			pprint(error)



