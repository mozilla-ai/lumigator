import json

import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx
import pulumi_eks as eks
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts

# Can't do parent imports
# from ..common import (
#     BUCKET_ID,
#     DATABASE_NAME,
#     DATABASE_PASSWORD,
#     DATABASE_URL,
#     DATABASE_USER,
#     KUBECONFIG,
#     REPOSITORY_URL,
#     SERVICE_ACCOUNT_NAME,
# )

# TODO Move to module
BACKEND_REPOSITORY_URL = "backend-repo-url"
JOB_RUNNER_REPOSITORY_URL = "jobrunner-repo-url"
KUBECONFIG = "kubeconfig"
SERVICE_ACCOUNT_NAME = "sa-name"
DATABASE_URL = "db-url"
DATABASE_NAME = "db-name"
DATABASE_USER = "db-user"
DATABASE_PASSWORD = "db-pass"
BUCKET_ID = "bucket-id"

backend_repository = awsx.ecr.Repository(
    "backend-repo",
    awsx.ecr.RepositoryArgs(force_delete=True),
)

pulumi.export(BACKEND_REPOSITORY_URL, backend_repository.url)

jobrunner_repository = awsx.ecr.Repository(
    "job-runner-repo",
    awsx.ecr.RepositoryArgs(force_delete=True),
)

pulumi.export(JOB_RUNNER_REPOSITORY_URL, backend_repository.url)

# Create a VPC for our cluster.
# vpc = awsx.ec2.Vpc("vpc")

# Note this creates three AZs and three nat gateways
#
# managed_policy_arns = [
#    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
#    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
#    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
# ]
# assume_role_policy = json.dumps(
#    {
#        "Version": "2012-10-17",
#        "Statement": [
#            {
#                "Action": "sts:AssumeRole",
#                "Effect": "Allow",
#                "Principal": {
#                    "Service": "ec2.amazonaws.com",
#                },
#            }
#        ],
#    }
# )
# node_group_role = aws.iam.Role(
#    "node-group-role",
#    assume_role_policy=assume_role_policy,
#    managed_policy_arns=managed_policy_arns,
# )
#
## instance_profile1 = aws.iam.InstanceProfile("instanceProfile1", role=node_group_role.name)
#
#
## Create an EKS cluster with the default configuration.
## Note needed to change region - Could not create in us-east-1
## See region set in .env file
## Cannot create cluster 'cluster-eksCluster-6d3eb4a' because EKS does not support creating control
## plane instances in us-east-1e, the targeted availability zone
## https://github.com/pulumi/pulumi-eks/issues/95
## https://github.com/eksctl-io/eksctl/issues/118
#
# Create an EKS cluster inside of the VPC.
## cluster = eks.Cluster(
##     "platform-cluster",
##     vpc_id=vpc.vpc_id,
##     public_subnet_ids=vpc.public_subnet_ids,
##     private_subnet_ids=vpc.private_subnet_ids,
##     node_associate_public_ip_address=False,
##     create_oidc_provider=True,
##     opts=pulumi.ResourceOptions(depends_on=[vpc]),
## )


## Create a node group
# managed_node_group = eks.ManagedNodeGroup(
#    "gpu-node-group",
#    cluster=cluster.name,
#    node_role_arn=node_group_role.arn,
#    subnet_ids=vpc.private_subnet_ids,
#    node_group_name="gpu-group",
#    scaling_config=aws.eks.NodeGroupScalingConfigArgs(
#        min_size=1,
#        desired_size=1,
#        max_size=1,
#    ),
#    instance_types=["g5.xlarge"],
#    disk_size=100,
#    ami_type="BOTTLEROCKET_x86_64_NVIDIA",
#    opts=pulumi.ResourceOptions(depends_on=[cluster]),
# )
#
#
## Export the cluster's kubeconfig.
# pulumi.export(KUBECONFIG, cluster.kubeconfig)
# cluster_provider = kubernetes.Provider(
#     "clusterProvider",
#     kubeconfig=cluster.kubeconfig,
#     enable_server_side_apply=True,
#     opts=pulumi.ResourceOptions(depends_on=[cluster]),
# )
## Get the name of the default namespace
# namespace = "default"
# sa_name = "platform-sa"
#
## https://www.pulumi.com/blog/eks-oidc/
## sub = cluster.core.oidc_provider.url.apply(lambda url: url + ":sub")
## https://github.com/pulumi/pulumi-aws/issues/2080
## Note the use of the "_output" version of the function here
## TODO Figure out a way to make this dependent on the Cluster being created (Looks like you can't set dependsOn on a 'get')
# eks_assume_role_policy = aws.iam.get_policy_document_output(
#    statements=[
#        aws.iam.GetPolicyDocumentStatementArgs(
#            actions=["sts:AssumeRoleWithWebIdentity"],
#            principals=[
#                aws.iam.GetPolicyDocumentStatementPrincipalArgs(
#                    type="Federated",
#                    identifiers=[cluster.core.oidc_provider.arn],
#                )
#            ],
#            effect="Allow",
#            conditions=[
#                # https://kubedemy.io/aws-eks-part-13-setup-iam-roles-for-service-accounts-irsa
#                # TODO: Add Audience condition
#                aws.iam.GetPolicyDocumentStatementConditionArgs(
#                    test="StringEquals",
#                    variable=cluster.core.oidc_provider.url.apply(lambda url: url + ":sub"),
#                    values=[f"system:serviceaccount:{namespace}:{sa_name}"],
#                )
#            ],
#        )
#    ]
# )
#
## source_json is deprecated: Not used
# eks_role = aws.iam.Role("eks_irsa_iam_role", assume_role_policy=eks_assume_role_policy.json)
#
## https://www.pulumi.com/registry/packages/aws/api-docs/iam/policy/
## Attach necessary policies to the IAM role
## TODO Lock down to specific bucket
# managed_policy_arns = [
#    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
# ]
# for policy_arn in managed_policy_arns:
#    aws.iam.RolePolicyAttachment(
#        f"eksPolicy-{policy_arn}", policy_arn=policy_arn, role=eks_role.name
#    )
#
## Create a Kubernetes Service Account in the default namespace
# service_account = kubernetes.core.v1.ServiceAccount(
#    "platform-sa",
#    metadata=kubernetes.meta.v1.ObjectMetaArgs(
#        name=sa_name,
#        namespace=namespace,
#        annotations={
#            "eks.amazonaws.com/role-arn": eks_role.arn,
#        },
#    ),
#    opts=pulumi.ResourceOptions(provider=cluster_provider, depends_on=[cluster, cluster_provider]),
# )
#
# pulumi.export(SERVICE_ACCOUNT_NAME, service_account.metadata.name)
#

## TODO create separate subnets for DB?
db_subnet_group = aws.rds.SubnetGroup(
    "platform-db-subnet-group",
    subnet_ids=[
        "subnet-089dca64cb5244510",
        "subnet-06b37f1c7abe85e48",
        "subnet-02da01ada8e96eb85",
    ],  # vpc.private_subnet_ids,
    # opts=pulumi.ResourceOptions(depends_on=[vpc])
)

## Create a Security Group that allows inbound (ingress) traffic on Port 5432 (default PostgreSQL port)
## TODO: Lock down to private subnets / kube nodes only
security_group = aws.ec2.SecurityGroup(
    "platform-db-sg",
    vpc_id="vpc-001dfcb15187ce7d8",  # From eksctl  # vpc.vpc_id,
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 5432,
            "to_port": 5432,
            "cidr_blocks": ["0.0.0.0/0"],
        }
    ],
)  # opts=pulumi.ResourceOptions(depends_on=[vpc]


db_name = "platform"
db_user = "db_admin"
db_pass = "password123"  # TODO Use Pulumi Secret

#
## Create a RDS instance
db_instance = aws.rds.Instance(
    "platform-db",
    engine="postgres",
    instance_class="db.t3.small",
    allocated_storage=20,
    db_name=db_name,
    username=db_user,
    password=db_pass,
    publicly_accessible=False,
    skip_final_snapshot=True,
    vpc_security_group_ids=[security_group.id],
    db_subnet_group_name=db_subnet_group.name,
    opts=pulumi.ResourceOptions(depends_on=[security_group, db_subnet_group]),
)

# pulumi.export(DATABASE_URL, db_instance.address)
# pulumi.export(DATABASE_NAME, db_name)
# pulumi.export(DATABASE_USER, db_user)
# pulumi.export(DATABASE_PASSWORD, db_pass)
#

# kube_ray = Chart(
#     "kuberay-operator",
#     ChartOpts(
#         chart="kuberay-operator",
#         version="1.1.0",
#         fetch_opts=FetchOpts(
#             repo="https://ray-project.github.io/kuberay-helm/",
#         ),
#     ),
#     opts=pulumi.ResourceOptions(provider=cluster_provider, depends_on=[cluster, cluster_provider]),
# )
bucket = aws.s3.Bucket("platform-data")

pulumi.export(BUCKET_ID, bucket.id)
#
## command = bucket.id.apply(
##    lambda id: f"curl -sL -o /s3-echoer https://git.io/JfnGX && chmod +x /s3-echoer && echo This is an in-cluster test | /s3-echoer {id} && sleep 3600"
## )
#
## pod = kubernetes.core.v1.Pod(
##    "test-pod",
##    metadata=kubernetes.meta.v1.ObjectMetaArgs(namespace=namespace),
##    spec=kubernetes.core.v1.PodSpecArgs(
##        service_account_name=service_account.metadata.name,
##        containers=[
##            kubernetes.core.v1.ContainerArgs(
##                name="my-pod",
##                image="amazonlinux:2018.03",
##                command=["sh", "-c", command],
##                env=[
##                    kubernetes.core.v1.EnvVarArgs(name="AWS_DEFAULT_REGION", value="us-east-2"),
##                    kubernetes.core.v1.EnvVarArgs(name="ENABLE_IRP", value="true"),
##                ],
##            ),
##        ],
##    ),
##    opts=pulumi.ResourceOptions(provider=cluster_provider, depends_on=[cluster, cluster_provider]),
## )
#
# kube_ray = Chart(
#    "ray-cluster",
#    ChartOpts(
#        chart="ray-cluster",
#        version="1.1.0",
#        fetch_opts=FetchOpts(
#            repo="https://ray-project.github.io/kuberay-helm/",
#        ),
#        values={
#            "image": {
#                "repository": "rayproject/ray-ml",
#                "tag": "2.23.0-py310-gpu",
#            },
#            "head": {
#                "resources": {
#                    "limits": {
#                        "nvidia.com/gpu": 1  # Required to use GPU.
#                    }
#                }
#            },
#        },
#    ),
#    opts=pulumi.ResourceOptions(provider=cluster_provider, depends_on=[cluster_provider]),
# )
