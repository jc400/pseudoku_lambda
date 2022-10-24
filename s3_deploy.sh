#!/bin/bash

#simple shell script to sync static files into AWS bucket 


AWS_endpoint="s3://pseudoku.jakobodev.com"
local_repo="./static"

if [ -d $local_repo ]; then
    aws s3 sync $local_repo $AWS_endpoint --delete
fi
