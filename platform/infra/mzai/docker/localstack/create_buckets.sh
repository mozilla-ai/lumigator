#!/usr/bin/env bash
for bucket in ${CREATE_BUCKETS//,/ }; do
    awslocal s3api create-bucket --bucket $bucket
done
