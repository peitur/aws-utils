#!/bin/python3.4
import os, sys, json, yaml

import memcache


class MemCacheClient():
	"""
		My test memcached client class, inteneded to be moved to a official tool lib
	"""


	def __init__( self, **options ):
		self.debug = False
		self.hostname = "127.0.0.1"
		self.port = "11211"
		self.expiry = 0
		
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

	def delete( self, key, val, **options ):
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



if __name__ == "__main__":
	m = MemCacheClient( debug=True )

	k0 = "test1"
	k1 = "test2"
	k2 = "test3"

	v0 = '{ "type":"web", "name":"web1.example.com", "ip":"10.1.1.121" }'
	v1 = '{ "type":"web", "name":"web2.example.com", "ip":"10.1.1.122" }'
	v2 = '{ "type":"web", "name":"web3.example.com", "ip":"10.1.1.123" }'

	m.set( k0, v0 )
	m.set( k1, v1, expiry=3600 )

	print("###################################################")
	print(">>>>> %(val)s" % { 'val': m.get( k0 ) }  )
	print(">>>>> %(val)s" % { 'val': m.get( k1 ) }  )
	print(">>>>> %(val)s" % { 'val': m.get( k2 ) }  )
	print("###################################################")
	
	jval = m.get( k1 , debug=False)
	if jval:
		data = json.loads( jval )
		val = yaml.dump( data, explicit_start=True, default_flow_style=False )
		print("%(val)s" % { 'val': val }  )
	else:
		print("No data in memcached")
