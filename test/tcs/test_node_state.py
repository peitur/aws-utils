import re, os, sys, pathlib, unittest, shlex, shutil, hashlib, datetime
sys.path.append(  pathlib.Path.cwd().__str__()+"/../lib")
sys.path.append(  pathlib.Path.cwd().__str__()+"/../../lib")

from pprint import pprint
import AwsUtils.state
import AwsUtils.utils


NODE_ROOT = "/tmp/ssd_test"
NODE_DATA = {
			"test0.node.json": {'addr': "127.0.0.1", 'type': "web" },
			"test1.node.json": {'addr': "127.0.0.1", 'type': "web", "key":"98977fb8ddc75b0ee3a69ef7805c65a403e39dd7cab2b74754c93ded" }, 
			"test2.node.json": {'addr': "127.0.0.1", 'type': "web", "key":"98977fb8ddc75b0ee3a69ef7805c65a403e39dd7cab2b74754c93dex" },
			"test3.node.json": {'type': "web" },
			"test4.node.json": {'addr': "127.0.0.1"},
			"test5.node.json": None			
		}

class TestNodeState( unittest.TestCase ):


	def setUp( self ):
		self.cwd = pathlib.Path.cwd().__str__()
		self.t_data = pathlib.Path.cwd().__str__()+"/t_data"

		self.nodes = NODE_DATA
		self.nstore = AwsUtils.state.NodeStore( NODE_ROOT, debug=False )




	def tearDown( self ):
		if pathlib.Path( NODE_ROOT ).exists(): shutil.rmtree( NODE_ROOT )


	def __initialize_files__( self ):
		for n in self.nodes:
			src_file = self.t_data+"/"+n
			dst_file = NODE_ROOT+"/nodes/"+n

			if pathlib.Path( src_file ).exists() : 
#				print( ">>>>>> %(src)s => %(dst)s" % { 'src': src_file, 'dst': dst_file } )
				shutil.copy( src_file, dst_file )

		return True

	def __xverification_key__( self, key , node ):

		xtime = int( datetime.datetime.utcnow().timestamp() )
		xterm = int( xtime / 10 )

		xstr = key+node+str( xterm )

		return hashlib.sha224( bytes( xstr , "ascii") ).hexdigest()



	def test_register( self ):
		"""
			Test the registration funcitonality
		"""
		self.__initialize_files__()


		self.assertIsNotNone( self.nstore.register_node( "test0.node.json", self.nodes['test0.node.json'] ) )
		self.assertEqual( self.nstore.register_node( "test1.node.json", self.nodes['test1.node.json'] ), "98977fb8ddc75b0ee3a69ef7805c65a403e39dd7cab2b74754c93ded" )
		self.assertNotEqual( self.nstore.register_node( "test1.node.json", self.nodes['test1.node.json'] ), "98977fb8ddc75b0ee3a69ef7805c65a403e39dd7cab2b74754c93dex" )

		with self.assertRaises(Exception):
			self.nstore.register_node( "test3.node.json", self.nodes['test3.node.json'] )

		with self.assertRaises(Exception):
			self.nstore.register_node( "test4.node.json", self.nodes['test4.node.json'] )

		with self.assertRaises(Exception):
			self.nstore.register_node( "test5.node.json", self.nodes['test5.node.json'] )


	def test_unregister( self ):

		node = 'test1.node.json'
		ok_key  = "98977fb8ddc75b0ee3a69ef7805c65a403e39dd7cab2b74754c93ded"
		not_key = "98977fb8ddc75b0ee3a69ef7805c65a403e39dd7cab2b74754c93dex"

		## Matching
		self.__initialize_files__()
		self.nodes = NODE_DATA

		self.assertEqual( self.nstore.register_node( node , self.nodes[ node ] ), ok_key )		
		refdata1 = {'addr': "127.0.0.1", 'type': "web" }
		refdata1['key'] = self.__xverification_key__( ok_key, node )
		self.assertTrue( self.nstore.unregister_node( node , refdata1 ) )
	
		## NOT Matching
		self.__initialize_files__()
		self.nodes = NODE_DATA

		self.assertEqual( self.nstore.register_node( node , self.nodes[ node ] ), ok_key )		
		refdata2 = {'addr': "127.0.0.1", 'type': "web" }
		refdata2['key'] = self.__xverification_key__( not_key, node )
		with self.assertRaises(Exception):
			self.nstore.unregister_node( node , refdata2 )


		self.assertIsNone( self.nstore.node_is_defined( 'test30.node.json' ) )
		self.assertIsNotNone( self.nstore.node_is_defined( 'test1.node.json' ) )
		self.assertIsNotNone( self.nstore.node_is_defined( 'test2.node.json' ) )


	def test_keyverification( self ):

		node = 'test1.node.json'
		ok_key  = "98977fb8ddc75b0ee3a69ef7805c65a403e39dd7cab2b74754c93ded"
		not_key = "98977fb8ddc75b0ee3a69ef7805c65a403e39dd7cab2b74754c93dex"

		## Matching
		self.__initialize_files__()
		self.nodes = NODE_DATA

		self.assertEqual( self.nstore.register_node( node , self.nodes[ node ] ), ok_key )		
		self.assertTrue( self.nstore.verify_key( self.__xverification_key__( ok_key, node ), node ) )
	
		## NOT Matching
		self.__initialize_files__()
		self.nodes = NODE_DATA

		self.assertEqual( self.nstore.register_node( node , self.nodes[ node ] ), ok_key )		
		self.assertFalse( self.nstore.verify_key( self.__xverification_key__( not_key, node ), node ) )


		self.assertIsNone( self.nstore.node_is_defined( 'test30.node.json' ) )
		self.assertIsNotNone( self.nstore.node_is_defined( 'test1.node.json' ) )
		self.assertIsNotNone( self.nstore.node_is_defined( 'test2.node.json' ) )





	def xtest_update( self ):
		pass

	def test_node_state( self ):
		"""
			Test the node status management
		"""
		self.__initialize_files__()
		self.nodes = NODE_DATA

		self.assertIsNotNone( self.nstore.register_node( "test10.node.json", self.nodes['test0.node.json'] ) )
		self.assertEqual( self.nstore.node_state( "test10.node.json" ), [] )

		self.assertIsNotNone( self.nstore.register_node( "test11.node.json", self.nodes['test0.node.json'] ) )
		self.assertEqual( self.nstore.node_state( "test11.node.json", "created" ), ["created"] )
		self.assertEqual( self.nstore.node_state( "test11.node.json", "started" ), ["started"] )
		pprint( self.nstore.node_state( "test11.node.json" ) )

#		self.assertIsNotNone( self.nstore.register_node( "test12.node.json", self.nodes['test1.node.json'] ) )
		with self.assertRaises(Exception):
			self.nstore.node_state( "test12.node.json", "badstate" )

		## Equals empty list as a dep. on previous tests that should not have taken effect
		self.assertEqual( self.nstore.node_state( "test12.node.json", None ), [] )

		self.assertFalse( self.nstore.node_state( "test12.node.json", "" ) )




	def xtest_key_gen( self ):
		pass







if __name__ == "__main__":
	unittest.main()