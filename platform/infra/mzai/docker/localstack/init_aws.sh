#!/usr/bin/env bash

# Create S3 buckets
# shellcheck disable=SC2001
for bucket in $(echo "$CREATE_BUCKETS" | sed "s/,/ /g"); do
	awslocal s3 mb "s3://$bucket"
done
