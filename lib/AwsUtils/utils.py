import json, yaml, os, sys, pathlib

def load_json( filename ):
		"""
		
		"""
		if not filename: raise RuntimeError( "ERROR: No configuration file")

		data = ""
		try:
			fd = open( filename, "r" )
			for line in fd:	
				data += line
			fd.close()

			return json.loads( data )
		except IOError as error:
			raise IOError("Could not open file "+error__str__() )
		except:
			raise

		return None


def save_json( filename, data, **options ):
		"""
			
		"""

		debug = False
		overwrite = False

		if 'debug' in options: debug = options['debug']
		if 'overwrite' in options: overwrite = options['overwrite']

		if(debug) : print("DEBUG[WriteJson]: F:%(filename)s : %(data)s : %(opt)s" % {'filename': filename, 'data': data, 'opt':options})

		if not filename or len( filename ) == 0:
			raise RuntimeError("No write file specified")
			

		if pathlib.Path( filename ).exists() and not overwrite: return False

		try:
			fd = open( filename, "w" )
			fd.write( json.dumps( data ) )
			fd.close()

			return True
		except IOError as error:
			print("ERROR[WriteJson]: %(error)s" % { 'error':error} )
			raise
		except:
			raise
			
		return None


