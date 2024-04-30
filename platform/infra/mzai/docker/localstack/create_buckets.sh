#!/usr/bin/env bash
for bucket in $(echo $CREATE_BUCKETS | sed "s/,/ /g"); do
    awslocal s3api create-bucket --bucket $bucket
done
