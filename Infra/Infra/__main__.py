import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx
import pulumi_eks as eks
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts

# Need IAM role on kube nodes?
repository = awsx.ecr.Repository(
    "repository",
    awsx.ecr.RepositoryArgs(force_delete=True),
)

pulumi.export("repo-url", repository.url)

# Create a VPC for our cluster.
vpc = awsx.ec2.Vpc("vpc")
# Note this creates three AZs and three nat gateways

# Create an EKS cluster with the default configuration.
# Note needed to change region - Could not create in us-east-1
# See region set in .env file
# Cannot create cluster 'cluster-eksCluster-6d3eb4a' because EKS does not support creating control
# plane instances in us-east-1e, the targeted availability zone
# https://github.com/pulumi/pulumi-eks/issues/95
# https://github.com/eksctl-io/eksctl/issues/118

# Create an EKS cluster inside of the VPC.
cluster = eks.Cluster(
    "cluster",
    vpc_id=vpc.vpc_id,
    public_subnet_ids=vpc.public_subnet_ids,
    private_subnet_ids=vpc.private_subnet_ids,
    node_associate_public_ip_address=False,
    create_oidc_provider=True,
    opts=pulumi.ResourceOptions(depends_on=[vpc]),
)

cluster_provider = kubernetes.Provider(
    "clusterProvider",
    kubeconfig=cluster.kubeconfig,
    enable_server_side_apply=True,
    opts=pulumi.ResourceOptions(depends_on=[cluster]),
)

cluster_oidc_provider_url = cluster.core.oidc_provider.url

pulumi.export("oidc_url", cluster_oidc_provider_url)

cluster_oidc_provider_arn = cluster.core.oidc_provider.arn

pulumi.export("oidc_arn", cluster_oidc_provider_arn)

# Use the OIDC provider URL to retrieve the OIDC provider ARN
# oidc_provider_arn = cluster.core.oidc_provider_url.apply(
#     lambda url: aws.iam.get_open_id_connect_provider(
#         arn=f"arn:aws:iam::{aws.get_caller_identity().account_id}:oidc-provider/{url.split('https://')[1]}"
#     )
# )

pulumi.export("oidc_url", cluster_oidc_provider_url)  # Exporting this value materializes the value

# Get the name of the default namespace
namespace = "default"

sa_name = "s3"

# Create the new IAM policy for the Service Account using the AssumeRoleWebWebIdentity action.
# May need to use pulumi.all here to materialize the values before they are used.
# Need to add `aud` to the conditions

sub = cluster.core.oidc_provider.url.apply(lambda url: url + ":sub")

pulumi.export("sub", sub)

eks_assume_role_policy = aws.iam.get_policy_document(
    statements=[
        aws.iam.GetPolicyDocumentStatementArgs(
            actions=["sts:AssumeRoleWithWebIdentity"],
            principals=[
                aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                    type="Federated",
                    identifiers=[cluster_oidc_provider_arn],
                )
            ],
            effect="Allow",
            conditions=[
                # https://kubedemy.io/aws-eks-part-13-setup-iam-roles-for-service-accounts-irsa
                # TODO: Look into "oidc.eks.eu-west-2.amazonaws.com/id/41C415204248C3A34377D6A4D103A9C8:aud": "sts.amazonaws.com",
                aws.iam.GetPolicyDocumentStatementConditionArgs(
                    test="StringEquals",
                    variable=sub,  # May need to remove "https" from URL
                    # Tried to use f"{url}:sub" but got the following error when inspecting the object: Calling __str__ on an Output[T] is not supported.\n\nTo get the value of an Output[T] as an Output[str] consider:\n1. o.apply(lambda v: f\"prefix{v}suffix\")\n\nSee https://www.pulumi.com/docs/concepts/inputs-outputs for more details.\nThis function may throw in a future version of Pulumi.:sub
                    values=[f"system:serviceaccount:{namespace}:{sa_name}"],
                )
            ],
        )
    ]
)
pulumi.export("policy_doc", eks_assume_role_policy)

# source_json is deprecated: Not used
eks_role = aws.iam.Role("eks_irsa_iam_role", assume_role_policy=eks_assume_role_policy.json)

# Attach necessary policies to the IAM role
managed_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
]
for policy_arn in managed_policy_arns:
    aws.iam.RolePolicyAttachment(
        f"eksPolicy-{policy_arn}", policy_arn=policy_arn, role=eks_role.name
    )

# Create a Kubernetes Service Account in the default namespace
service_account = kubernetes.core.v1.ServiceAccount(
    "test-sa",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name=sa_name,
        namespace=namespace,
        annotations={
            "eks.amazonaws.com/role-arn": eks_role.arn,
        },
    ),
    opts=pulumi.ResourceOptions(provider=cluster_provider, depends_on=[cluster, cluster_provider]),
)

# Export the cluster's kubeconfig.
pulumi.export("kubeconfig", cluster.kubeconfig)

# Just use private subnets from VPC, or create separate subnets for DB?
db_subnet_group = aws.rds.SubnetGroup(
    "new-db-subnet-group",
    subnet_ids=vpc.private_subnet_ids,
    opts=pulumi.ResourceOptions(depends_on=[vpc]),
)

# Create a Security Group that allows inbound (ingress) traffic on Port 5432 (default PostgreSQL port)
# TODO: Lock down to private subnets / kube nodes only
security_group = aws.ec2.SecurityGroup(
    "db-sg",
    vpc_id=vpc.vpc_id,
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 5432,
            "to_port": 5432,
            "cidr_blocks": ["0.0.0.0/0"],
        }
    ],
    opts=pulumi.ResourceOptions(depends_on=[vpc]),
)

db_name = "mydatabase"
pg_user = "db_admin"
pg_pass = "password123"
## Create a RDS instance
db_instance = aws.rds.Instance(
    "db-instance",
    engine="postgres",
    instance_class="db.t3.small",
    allocated_storage=20,
    db_name=db_name,
    username=pg_user,
    password=pg_pass,  # TODO Pulumi Secrets
    publicly_accessible=False,
    skip_final_snapshot=True,
    vpc_security_group_ids=[security_group.id],
    db_subnet_group_name=db_subnet_group.name,
    opts=pulumi.ResourceOptions(depends_on=[security_group, db_subnet_group]),
)


pulumi.export("db-url", db_instance.address)

kube_ray = Chart(
    "kuberay-operator",
    ChartOpts(
        chart="kuberay-operator",
        version="1.1.0",
        fetch_opts=FetchOpts(
            repo="https://ray-project.github.io/kuberay-helm/",
        ),
    ),
    opts=pulumi.ResourceOptions(provider=cluster_provider, depends_on=[cluster, cluster_provider]),
)

bucket = aws.s3.Bucket("pod-irsa-job-bucket")

command = bucket.id.apply(
    lambda id: f"curl -sL -o /s3-echoer https://git.io/JfnGX && chmod +x /s3-echoer && echo This is an in-cluster test | /s3-echoer {id} && sleep 3600"
)

# pulumi.export("command", command)

# s3_pod = kubernetes.core.v1.Pod(
#    "test-pod",
#    metadata=kubernetes.meta.v1.ObjectMetaArgs(namespace=namespace),
#    spec=kubernetes.core.v1.PodSpecArgs(
#        service_account_name=service_account.metadata.name,
#        containers=[
#            kubernetes.core.v1.ContainerArgs(
#                name="my-pod",
#                image="amazonlinux:2018.03",
#                command=["sh", "-c", command],
#                env=[
#                    kubernetes.core.v1.EnvVarArgs(name="AWS_DEFAULT_REGION", value="us-east-2"),
#                    kubernetes.core.v1.EnvVarArgs(name="ENABLE_IRP", value="true"),
#                ],
#            ),
#        ],
#    ),
#    opts=pulumi.ResourceOptions(provider=cluster_provider, depends_on=[cluster, cluster_provider]),
# )
