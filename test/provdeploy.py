#!/bin/python3.4

import re, os, sys
import shlex, time, datetime
import json, yaml
import subprocess, multiprocessing

from pprint import pprint

from flask import Flask, session, request

app = Flask( __name__ )


def provision_node( data = {} ):
	command = ["ip", "addr" ]
	
	log = open( "/tmp/test.log", "w")

#	command.append( "/bin/echo" )
#	command.append( "'%()s'" )

	with subprocess.Popen( command, stdout=subprocess.PIPE) as proc:
	    log.write( "%(out)s" % { 'out': proc.stdout.read().decode("ascii") } )

	time.sleep( 2000 )

## 
# curl -H "Content-Type: application/json" -X POST -d '{"request":"deploy", "type":"web","priv_ip":"10.11.12.12", "publ_ip":"123.113.123.123", "pki":"test"}' http://192.168.56.80:8080/register

@app.route('/register', methods=['GET', 'POST'])
def provision_node(  ):

	if request.method == 'POST':

		config = {}
		form = request.get_json( force=True )

		if 'request' in form: config['request'] = form['request']
		if 'name' in form: config['name'] = form['name']
		if 'hostname' in form: config['hostname'] = form['hostname']
		if 'type' in form: config['type'] = form['type']
		if 'publ_ip' in form: config['publ_ip'] = form['publ_ip']
		if 'priv_ip' in form: config['priv_ip'] = form['priv_ip']
		if 'pki' in form: config['pki'] = form['pki']

		if config['publ_ip'] and not config['priv_ip']:
			config['priv_ip'] = config['publ_ip']

		if config['priv_ip'] and not config['publ_ip']:
			config['publ_ip'] = config['priv_ip']


		if   not config['hostname']: return '{ "result": "500", "type":"'+request.method+'", "message":"missing hostname" }'
		elif not config['name']: return '{ "result": "500", "type":"'+request.method+'", "message":"missing name" }'
		elif not config['priv_ip'] and not config['publ_ip']: return '{ "result": "500", "type":"'+request.method+'", "message":"missing priv_ip or publ_ip" }'
		elif not config['pki']: return '{ "result": "500", "type":"'+request.method+'", "message":"missing private key " }'
		elif not config['type']: return '{ "result": "500", "type":"'+request.method+'", "message":"missing host type" }'
		else:
			p = multiprocessing.Process( target=provision_node, args=( config, ) )
			return '{ "result": "200", "type":"'+request.method+'", "message":"'+ json.dumps( config ) +'" }'


	return '{ "result": "200", "type":"'+request.method+'"}'


if __name__ == "__main__":
	app.debug=True
	app.run( host='0.0.0.0', port=8080 )
