#!/bin/python3.4

import re, os, sys
import shlex, time, datetime
import json, yaml
import subprocess, multiprocessing

from pprint import pprint

import memcache


class MemCacheClient():
	"""
		My test memcached client class, inteneded to be moved to a official tool lib
	"""


	def __init__( self, **options ):
		self.debug = False
		self.hostname = "127.0.0.1"
		self.port = "11211"
		self.expiry = 3600
		
		self.client = None

		if "debug" in options: self.debug = options['debug']
		if "hostname" in options: self.hostname = options['hostname']
		if "port" in options: self.port = options['port']
		if "expiry" in options: self.expiry = options['expiry']

		connectstr = "%s:%s" % ( self.hostname, self.port )
		self.client = memcache.Client( [ connectstr ] )

		if self.debug:
			print("DEBUG: Init Debug:%(debug)s Hostname:%(hname)s Port:%(port)s Expiry:%(expiry)s" % { 'debug': self.debug,'hname': self.hostname,'port': self.port, 'expiry': self.expiry } )



	def add( self, key, val, **options ):
		"""
			Add Data
		"""

		debug = self.debug
		if "debug" in options: debug = options['debug']

		expiry = self.expiry
		if "expiry" in options: expiry = options['expiry']

		if debug: print("DEBUG: Add %(key)s : %(val)s Exp:%(exp)s " % {'key': key, 'val': val, 'exp': expiry } )

		self.client.add( key, val, expiry )


	def set( self, key, val, **options ):
		"""
			Set Data
		"""

		debug = self.debug
		if "debug" in options: debug = options['debug']

		expiry = self.expiry
		if "expiry" in options: expiry = options['expiry']

		if debug: print("DEBUG: Set %(key)s : %(val)s Exp:%(exp)s " % {'key': key, 'val': val, 'exp': expiry } )

		self.client.set( key, val, expiry )

	def delete( self, key, **options ):
		"""
			Delete Data
		"""

		debug = self.debug
		if "debug" in options: debug = options['debug']

		if debug: print("DEBUG: Delete %(key)s " % { 'key': key } )

		if self.client: self.client.delete( key )


	def get( self, key, **options ):
		"""
			Get Data
		"""
		debug = self.debug
		if "debug" in options: debug = options['debug']

		if debug: print("DEBUG: Get %(key)s " % { 'key': key } )

		if self.client:
			return self.client.get( key )

		return None


#######################################################################
def node_register( data = {} ):

	debug = True
	if 'debug' in data: debug = data['debug']

	config = {}
	config['type']='default'
	config['priv_ip']=None
	config['publ_ip']=None
	config['name']=None
	config['state']=None
	config['pki_name']=None
	config['pki_file']=None

	if 'type' in data: config['type'] = data['type']

	if 'priv_ip' in data: 
		config['priv_ip'] = data['priv_ip']
	else: 
		raise RuntimeError("Missing Private IP")

	if 'publ_ip' in data: 
		config['publ_ip'] = data['publ_ip']
	else:
		raise RuntimeError("Missing Public IP")

	if 'name' in data: config['name'] = data['name']
	if 'state' in data: config['state'] = data['state']
	if 'pki_name' in data: config['pki_name'] = data['pki_name']
	if 'pki_file' in data: config['pki_file'] = data['pki_file']

	config['timestamp'] = datetime.datetime.now().__str__()
	if 'timestamp' in data: config['timestamp'] = data['timestamp']

	if not config['name']:
		config['name'] = "%s-%s" % ( config['type'], "-".join( re.split( "\.", config['priv_ip'] ) ) )

	if debug:
		print("DEBUG: Register node >>")
		pprint( config )
		print("<<<<<<<<<<<<<<<<<<<<<<<")		


	m = MemCacheClient( debug=debug )
	nexists = m.get( config['name'] )
	if not nexists:
		print("[%(now)s] Provisioning node %(node)s" % { 'node': config['name'], 'now': config['timestamp'] } )

	m.set( config['name'], json.dumps( config ) )






def node_unregister( data = {} ):

	debug = False
	name = None

	if 'debug' in data: debug = data['debug']
	if 'name' in data: name = data['name']

	if name:
		m = MemCacheClient( debug=debug )
		m.delete( name )



def node_list( data =  {} ):
	pass


def node_details( data = {} ):
	debug = False
	name = None

	if 'debug' in data: debug = data['debug']
	if 'name' in data: name = data['name']

	if name:
		m = MemCacheClient( debug=debug )
		return m.get( name )



if __name__ == '__main__':

	CMD=["/bin/ls","-al","/tmp"]

	print(">>>>> ADDING >>>>>>>>>")
	reg_plist=[]
	reg_plist.append( multiprocessing.Process( target=node_register, args=({'type':'web', 'publ_ip':"113.123.123.123", 'priv_ip':"10.11.12.13", 'pki_file':'test.pem', 'debug':True},) ) )
	reg_plist.append( multiprocessing.Process( target=node_register, args=({'type':'web', 'publ_ip':"123.123.123.123", 'priv_ip':"10.21.12.13", 'pki_file':'test.pem', 'debug':True},) ) )
	reg_plist.append( multiprocessing.Process( target=node_register, args=({'type':'web', 'publ_ip':"133.123.123.123", 'priv_ip':"10.31.12.13", 'pki_file':'test.pem', 'debug':True},) ) )
	reg_plist.append( multiprocessing.Process( target=node_register, args=({'type':'db',  'publ_ip':"143.123.123.123", 'priv_ip':"10.41.12.13", 'pki_file':'test.pem', 'debug':True},) ) )
	reg_plist.append( multiprocessing.Process( target=node_register, args=({'type':'elb', 'publ_ip':"153.123.123.123", 'priv_ip':"10.51.12.13", 'pki_file':'test.pem', 'debug':True},) ) )


	for p in reg_plist: p.start()
	for p in reg_plist: p.join()

	print(">>>>> ADDED  >>>>>>>>>")

	pprint( node_details( { 'name':"web-10-11-12-13"} ) )
	pprint( node_details( { 'name':"web-10-21-12-13"} ) )
	pprint( node_details( { 'name':"web-10-31-12-13"} ) )
	pprint( node_details( { 'name':"web-10-41-12-13"} ) )
	pprint( node_details( { 'name':"web-10-51-12-13"} ) )
	pprint( node_details( { 'name':"db-10-41-12-13"} ) )
	pprint( node_details( { 'name':"elb-10-51-12-13"} ) )

	print("<<<<<<<<<<<<<<<<<<<<<<<<<")

	print(">>>>> DELETING >>>>>>>>>")

	ureg_plist = []
	ureg_plist.append( multiprocessing.Process( target=node_unregister, args=( {'name':'web-10-11-12-13'},) ) )
	ureg_plist.append( multiprocessing.Process( target=node_unregister, args=( {'name':'web-10-21-12-13'},) ) )
	ureg_plist.append( multiprocessing.Process( target=node_unregister, args=( {'name':'web-10-31-12-13'},) ) )
	ureg_plist.append( multiprocessing.Process( target=node_unregister, args=( {'name':'web-10-41-12-13'},) ) )
	ureg_plist.append( multiprocessing.Process( target=node_unregister, args=( {'name':'web-10-51-12-13'},) ) )
	ureg_plist.append( multiprocessing.Process( target=node_unregister, args=( {'name':'db-10-41-12-13'},) ) )
	ureg_plist.append( multiprocessing.Process( target=node_unregister, args=( {'name':'elb-10-51-12-13'},) ) )


	for p in ureg_plist: p.start()
	for p in ureg_plist: p.join()

	print(">>>>> DELETED >>>>>>>>>")	

	pprint( node_details( { 'name':"web-10-11-12-13"} ) )
	pprint( node_details( { 'name':"web-10-21-12-13"} ) )
	pprint( node_details( { 'name':"web-10-31-12-13"} ) )
	pprint( node_details( { 'name':"web-10-41-12-13"} ) )
	pprint( node_details( { 'name':"web-10-51-12-13"} ) )
	pprint( node_details( { 'name':"db-10-41-12-13"} ) )
	pprint( node_details( { 'name':"elb-10-51-12-13"} ) )

	print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

#	with subprocess.Popen(["ip","addr"], stdout=subprocess.PIPE) as proc:
#	    print("%(out)s" % { 'out': proc.stdout.read().decode("ascii") } )







