#!/usr/bin/python3.4

import sys, os, json, yaml, getopt, re
import paramiko

from pprint import pprint

AVG_FILE="/proc/loadavg" 
UPTIME_FILE="/proc/uptime"
MEMINFO_FILE="/proc/meminfo"
FORMATS = ['text','json','yaml']


def load_sitefile( filename, debug = False ):
	
	default_pem = None
	default_user = None
	result = []

	try:
		fd = open( filename, "r" )
		for line in fd:

			if re.match( r"^\s*#", line ): break

			## format : host  user   pem
			lline = line.split()
			if   lline[0] == 'DEFAULT_USER': default_user = lline[1]
			elif lline[0] == 'DEFAULT_PEM': default_pem = lline[1]
			else:

				user = default_user
				pemfile = default_pem
				if len( lline ) > 1 and lline[1] : user = lline[1]
				if len( lline ) > 2 and lline[2] : pemfile = lline[2]

				result.append( { 'host': lline[0], 'user': user, 'pemfile': pemfile } )

		fd.close()

	except Exception as error:
		raise

	return result

def conenct( host, user, pemfile, debug = False ):

	if not os.path.exists( pemfile ):
		raise RuntimeError( "ERROR: No private key file %(pem)s" % { 'pem': pemfile } )

	try:
		pemref = paramiko.RSAKey.from_private_key_file( pemfile )

		client = paramiko.SSHClient()
		client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
		if debug: print( "DEBUG: Connecting to %(host)s with %(user)s using %(pem)s" % { 'host': host,'user': user, 'pem': pemfile} )
		ret =  client.connect( hostname=host, username=user, key_filename=pemfile, timeout=10 )
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



########################################
if __name__ == "__main__":


	script = sys.argv.pop(0)

	try:
		optlist, args = getopt.getopt( sys.argv , "ds:h:u:p:F:", ['debug','site=','user=','pem=','host=','format='])
	except getopt.GetoptError as err:
		print("Options: %(error)s" % { 'error': err.__str__() } )
		sys.exit(1)

	debug = False
	user = None
	pemfile = None
	host = None
	sitefile = None
	format = 'text'

	for opt, arg in optlist:
		if( opt   in ("-d","--debug" ) ): debug = True
		elif( opt in ("-u","--user" ) ): user = arg
		elif( opt in ("-p","--pem" ) ): pemfile = arg
		elif( opt in ("-h","--host" ) ): host = arg
		elif( opt in ("-s","--site" ) ): sitefile = arg
		elif( opt in ("-F","--format" ) ): format = arg


	if format not in FORMATS:
		print("Unsupported output format %(f)s" % { 'f':format } )
		sys.exit(0)

	conlist = []
	if sitefile:
		conlist = load_sitefile( sitefile, debug )

	if host and pemfile and user:
		conlist.append( { "host": host, "pemfile": pemfile, "user": user } )

	prep=""
	for hdata in conlist:
		try:
			if debug: print("Connecting to %(h)s" % {'h': hdata['host'] } )
			con = conenct( hdata['host'], hdata['user'], hdata['pemfile'], debug )

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



