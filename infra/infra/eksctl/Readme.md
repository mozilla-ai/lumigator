
https://github.com/eksctl-io/eksctl/issues/6229

```
docker logout public.ecr.aws
```


```
eksctl create cluster -f gpu.yaml
```

```
eksctl utils associate-iam-oidc-provider --region=us-east-2 --cluster=cluster-with-gpu --approve
```


```
eksctl create iamserviceaccount --cluster=cluster-with-gpu --name=s3 --namespace=default --attach-policy-arn=arn:aws:iam::aws:policy/AmazonS3FullAccess --approve
```

Setting up DB Subnet groups
https://aws.amazon.com/blogs/database/deploy-amazon-rds-databases-for-applications-in-kubernetes/


```
aws eks describe-cluster --name="cluster-with-gpu" --query "cluster.resourcesVpcConfig.vpcId" --output text
```


```
helm install kuberay-operator kuberay/kuberay-operator --version 1.1.1
```

```
helm install raycluster kuberay/ray-cluster --version 1.1.1 -f ray-cluster.yaml
```
