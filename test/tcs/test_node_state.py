import re, os, sys, pathlib, unittest, shlex, shutil
sys.path.append(  pathlib.Path.cwd().__str__()+"/../lib")
sys.path.append(  pathlib.Path.cwd().__str__()+"/../../lib")

from pprint import pprint
import AwsUtils.state


NODE_ROOT = "/tmp/ssd_test"

class TestNodeState( unittest.TestCase ):


	def setUp( self ):
		self.cwd = pathlib.Path.cwd().__str__()
		self.t_data = pathlib.Path.cwd().__str__()+"/t_data"

		self.nodes = {
			"test0.node.json": {'addr': "127.0.0.1", 'type': "web" },
			"test1.node.json": {'addr': "127.0.0.1", 'type': "web", "key":"98977fb8ddc75b0ee3a69ef7805c65a403e39dd7cab2b74754c93ded" }, 
			"test2.node.json": {'addr': "127.0.0.1", 'type': "web", "key":"98977fb8ddc75b0ee3a69ef7805c65a403e39dd7cab2b74754c93dex" },
			"test3.node.json": {'type': "web" },
			"test4.node.json": {'addr': "127.0.0.1"},
			"test5.node.json": None			
		}

		self.nstore = AwsUtils.state.NodeStore( NODE_ROOT, debug=True )

		for n in self.nodes:
			src_file = self.t_data+"/"+n
			dst_file = NODE_ROOT+"/nodes/"+n

			if pathlib.Path( src_file ).exists() : shutil.copy( src_file, dst_file )


	def tearDown( self ):

		if pathlib.Path( NODE_ROOT ).exists(): shutil.rmtree( NODE_ROOT )


	def test_register( self ):

		self.assertIsNotNone( self.nstore.register_node( "test0.node.json", self.nodes['test0.node.json'] ) )
		self.assertEqual( self.nstore.register_node( "test1.node.json", self.nodes['test1.node.json'] ), "98977fb8ddc75b0ee3a69ef7805c65a403e39dd7cab2b74754c93ded" )
		self.assertNotEqual( self.nstore.register_node( "test1.node.json", self.nodes['test1.node.json'] ), "98977fb8ddc75b0ee3a69ef7805c65a403e39dd7cab2b74754c93dex" )

		with self.assertRaises(Exception):
			self.nstore.register_node( "test3.node.json", self.nodes['test3.node.json'] )

		with self.assertRaises(Exception):
			self.nstore.register_node( "test4.node.json", self.nodes['test4.node.json'] )

		with self.assertRaises(Exception):
			self.nstore.register_node( "test5.node.json", self.nodes['test5.node.json'] )


	def xtest_unregister( self ):
		pass

	def xtest_update( self ):
		pass

	def xtest_node_state( self ):
		pass

	def xtest_key_gen( self ):
		pass



if __name__ == "__main__":
	unittest.main()