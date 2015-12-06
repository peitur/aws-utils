#!/usr/bin/bash

## Push a list of files to s3 through the aws cli command interface.

## Tool takes a list of files or a file with file references and uploads the files one at a time to s3


if [ ! $1 ] || [ ! $2 ] ; then
	echo "Need a reference file and a target bucket name"
	exit
else
	echo "Copying files from $1 to $2"
fi

echo "================================================="
while read p; do

	if [ -f $p ]; then
		# https://s3.amazonaws.com/pb-bucket1/Deployment/puppet/agent-installer.sh
		echo "aws s3 cp ${p} s3://${2}/${p}" # => https://s3.amazonaws.com/${2}"
	else

		echo "${p} doas not exist"
		
	fi

done < $1
echo "================================================="