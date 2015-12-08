import shlex, time, datetime
import json, yaml
import hashlib, pathlib
import subprocess, multiprocessing

import AwsUtils.utils

################################################
NODE_STORE  = 'nodes'
NODE_STATES = [ 'created', 'started' ,'running','stopped','provisioning','broken']
VERIFICATION_TIME = 10

class NodeStore:

	def __init__( self, path, **opt ):
		"""

		"""
		self.debug = False
		self.verification_time = VERIFICATION_TIME

		if 'debug' in opt: self.debug = opt['debug']
		if self.debug: print("Created NodeStore at %(s)s" % { 's': path } )

		self.rootpath = path
		p = pathlib.Path( self.rootpath )
		if not p.exists() :
			p.mkdir( parents=True )
			
			pathlib.Path( self.rootpath+"/"+NODE_STORE ).mkdir( parents=True )			
			
			for x in NODE_STATES:
				a = pathlib.Path( self.rootpath+"/"+x )
				if not a.exists() : a.mkdir( parents=True )


	def register_node( self, node, data = {} ):

		debug = self.debug

		if not node: raise RuntimeError("ERROR: Missing node name")
		if "addr" not in data: raise RuntimeError("ERROR: Missing node address")
		if "type" not in data: raise RuntimeError("ERROR: Missing node type")

		filename = self.rootpath+"/"+NODE_STORE+"/"+node

		if pathlib.Path( filename ).exists() :

			olddata = AwsUtils.utils.load_json( filename )

			## Already active ndoe, just sent a new registration request
			if 'key' in data and 'key' in olddata and data['key'] == olddata['key']:
				return olddata['key'] ## Only trust data on server

			elif 'key' not in data and 'key' in olddata:
				return olddata['key'] ## Only trust data on server

			## Node has old name and has different key, must be a different node
			elif 'key' in data and 'key' in olddata and data['key'] != olddata['key']:
				return None

		else:
			data['key'] = self.__gen_key__( node, data['addr'], data['type'] )
			AwsUtils.utils.save_json( filename, data )
			return data['key']



	def node_state( self, node, state = None ):
		"""

		"""

		if state :
			self.__set_node_state__( node, state )

		return self.__get_node_state__( node )


	def unregister_node( self, node, data = {} ):
		"""

		"""

		debug = self.debug
		filename = self.rootpath+"/"+NODE_STORE+"/"+node

		nodedata = AwsUtils.utils.load_json( filename )
		if 'key' not in data: raise RuntimeError( "Missing key in node indata")
		if 'key' not in nodedata: raise RuntimeError( "Missing key in node store")

		if self.__verification_key__( nodedata['key'], node ) != data['key']:
			raise RuntimeError( "Missmatching keys from node")


		for f in NODE_STATES:
			fname = self.rootpath+"/"+f+"/"+node
			if pathlib.Path( fname ).exists(): os.unlink( fname )

		if pathlib.Path( filename ).exists(): os.unlink( filename )


		return True


	def update_node( self, node, data = {} ):
		pass



	def valid_states( self ):
		return NODE_STATES


	def __set_node_state__( self, node, state ):
		"""
		"""



		debug = self.debug
		filename = self.rootpath+"/"+NODE_STORE+"/"+node

		if not state: raise RuntimeError("State is False/None")
		if state and len( state ) == 0: raise RuntimeError("Empty state string")		
		if state not in NODE_STATES: raise RuntimeError("Bad state given")

		## Lets create the new link state
		if state and pathlib.Path( filename ).exists() and not pathlib.Path( filename ).is_symlink():	
			sfname = self.rootpath+"/"+state+"/"+node
			pathlib.Path( sfname ).symlink_to( filename )
		else:
			return False

		## Cleanout all old states, exceopt for the requested state
		for s in NODE_STATES:
			sfname = self.rootpath+"/"+s+"/"+node
			if s != state and pathlib.Path( sfname ).exists() and pathlib.Path( sfname ).is_symlink():	
				pathlib.Path( sfname ).unlink()


		return True



	def __get_node_state__( self, node ):
		"""

		"""

		debug = self.debug
		filename = self.rootpath+"/"+NODE_STORE+"/"+node

		states = []
		for f in NODE_STATES:
			if pathlib.Path( self.rootpath+"/"+f+"/"+node ).exists(): states.append( f )

		return states





	def __gen_key__( self, node, addr, ntype ):
		now = str( int( datetime.datetime.utcnow().timestamp() ) )
		xstr = node+addr+ntype+now

		return hashlib.sha224( bytes( xstr , "ascii") ).hexdigest()

	def __verification_key__( self, key , node ):		
		xtime = int( datetime.datetime.utcnow().timestamp() )
		xterm = xtime / self.verification_time

		xstr = key+node+str( xterm )

		return hashlib.sha224( bytes( xstr , "ascii") ).hexdigest()

	def div_val( self ):
		return self.verification_time



