import re, os, sys, pathlib, unittest
sys.path.append(  pathlib.Path.cwd().__str__()+"/../lib")
sys.path.append(  pathlib.Path.cwd().__str__()+"/../../lib")

from pprint import pprint
import AwsUtils.utils

class TestUtils( unittest.TestCase ):


	def setUp( self ):

		self.cwd = pathlib.Path.cwd().__str__()
		self.t_data = pathlib.Path.cwd().__str__()+"/t_data"

		self.ok_file = self.t_data+"/file.json"
		self.nok_file = self.t_data+"/badfile.json"
		self.missing_file = self.t_data+"/missing.json"

		self.write_file = self.t_data+"/wrote.json"

	def tearDown( self ):
		if pathlib.Path( self.write_file ).exists(): os.unlink( self.write_file )

		pass

	def test_loading( self ):
		self.assertIsNotNone( AwsUtils.utils.load_json( self.ok_file ) )

		with self.assertRaises(Exception):
			AwsUtils.utils.load_json( self.bad_file )

		with self.assertRaises(Exception):
			AwsUtils.utils.load_json( self.missing_file )

	def test_save( self ):

		self.assertTrue( AwsUtils.utils.save_json( self.write_file, '{ "aaa":"AAA" }', overwrite=False ) )
		self.assertFalse( AwsUtils.utils.save_json( self.write_file, '{ "bbb":"BBB" }', overwrite=False ) )
		self.assertTrue( AwsUtils.utils.save_json( self.write_file, '{"ccc":"CCC"}', overwrite=True ) )

		with self.assertRaises(Exception):
			AwsUtils.utils.save_json( None )

		with self.assertRaises(Exception):
			AwsUtils.utils.save_json( "" )

		self.assertNotEqual( AwsUtils.utils.load_json( self.write_file ), '{"bbb":"BBB"}' )
		self.assertEqual( AwsUtils.utils.load_json( self.write_file ), '{"ccc":"CCC"}' )




if __name__ == "__main__":

	unittest.main()