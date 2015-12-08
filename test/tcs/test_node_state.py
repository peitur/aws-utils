import re, os, sys, pathlib, unittest
sys.path.append(  pathlib.Path.cwd().__str__()+"/../lib")


class TestNodeState( unittest.TestCase ):


	def setUp( self ):
		self.nodes = [ 
			{ "test1": {'addr': "127.0.0.1", 'type': "web", "key":"98977fb8ddc75b0ee3a69ef7805c65a403e39dd7cab2b74754c93ded" } }, 
			{ "test2": {'addr': "127.0.0.1", 'type': "web" } },
			{ "test1": {'addr': "127.0.0.1", 'type': "web", "key":"98977fb8ddc75b0ee3a69ef7805c65a403e39dd7cab2b74754c93dex" } } 
		]


	def tearDown( self ):
		pass




if __name__ == "__main__":
	unittest.main()