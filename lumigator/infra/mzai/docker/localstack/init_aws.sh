#!/usr/bin/env bash

# Create S3 buckets
for bucket in ${CREATE_BUCKETS//,/ }; do
	awslocal s3 mb s3://"$bucket"
done
