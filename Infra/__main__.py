"""An AWS Python Pulumi program"""

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
# Cannot create cluster 'cluster-eksCluster-6d3eb4a' because EKS does not support creating control plane instances in us-east-1e, the targeted availability zone
# https://github.com/pulumi/pulumi-eks/issues/95
# https://github.com/eksctl-io/eksctl/issues/118

# Create an EKS cluster inside of the VPC.
cluster = eks.Cluster(
    "cluster",
    vpc_id=vpc.vpc_id,
    public_subnet_ids=vpc.public_subnet_ids,
    private_subnet_ids=vpc.private_subnet_ids,
    node_associate_public_ip_address=False,
    opts=pulumi.ResourceOptions(depends_on=[vpc]),
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

cluster_provider = kubernetes.Provider(
    "clusterProvider",
    kubeconfig=cluster.kubeconfig,
    enable_server_side_apply=True,
    opts=pulumi.ResourceOptions(depends_on=[cluster]),
)


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

# helm install raycluster kuberay/ray-cluster --version 1.1.0
# TODO Get ray head svc address as output
# TODO Replace with CRD directly
kube_ray = Chart(
    "ray-cluster",
    ChartOpts(
        chart="ray-cluster",
        version="1.1.0",
        fetch_opts=FetchOpts(
            repo="https://ray-project.github.io/kuberay-helm/",
        ),
        values={
            "image": {
                "repository": "381492205691.dkr.ecr.us-east-2.amazonaws.com/repository-004e6f0",
                "tag": "job-runner-0.1",
            },
            "common": {
                "containerEnv": [
                    {"name": "BACKEND_HOST", "value": "backend-svc"},
                    {"name": "BACKEND_PORT", "value": "80"},
                ],
            },
        },
    ),
    opts=pulumi.ResourceOptions(provider=cluster_provider, depends_on=[cluster, cluster_provider]),
)

my_deployment = kubernetes.apps.v1.Deployment(
    "backend-deployment",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        labels={
            "appClass": "my-deployment",
        },
    ),
    spec=kubernetes.apps.v1.DeploymentSpecArgs(
        replicas=2,
        selector=kubernetes.meta.v1.LabelSelectorArgs(
            match_labels={
                "appClass": "my-deployment",
            },
        ),
        template=kubernetes.core.v1.PodTemplateSpecArgs(
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                labels={
                    "appClass": "my-deployment",
                },
            ),
            spec=kubernetes.core.v1.PodSpecArgs(
                containers=[
                    kubernetes.core.v1.ContainerArgs(
                        name="my-deployment",
                        image="381492205691.dkr.ecr.us-east-2.amazonaws.com/repository-004e6f0:backend-0.1",  # nginx
                        ports=[
                            kubernetes.core.v1.ContainerPortArgs(
                                name="http",
                                container_port=80,
                            )
                        ],
                        env=[
                            kubernetes.core.v1.EnvVarArgs(name="POSTGRES_DB", value=db_name),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_HOST", value=db_instance.address
                            ),
                            kubernetes.core.v1.EnvVarArgs(name="POSTGRES_USER", value=pg_user),
                            kubernetes.core.v1.EnvVarArgs(name="POSTGRES_PASSWORD", value=pg_pass),
                            kubernetes.core.v1.EnvVarArgs(name="POSTGRES_PORT", value="5432"),
                            kubernetes.core.v1.EnvVarArgs(
                                name="RAY_HEAD_NODE_HOST", value="ray-cluster-kuberay-head-svc"
                            ),
                            kubernetes.core.v1.EnvVarArgs(name="RAY_DASHBOARD_PORT", value="8265"),
                        ],
                    )
                ],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(provider=cluster_provider, depends_on=[cluster, cluster_provider]),
)

my_service = kubernetes.core.v1.Service(
    "backend-service",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="backend-svc",
        labels={
            "appClass": "my-deployment",
        },
    ),
    spec=kubernetes.core.v1.ServiceSpecArgs(
        type="LoadBalancer",
        ports=[
            kubernetes.core.v1.ServicePortArgs(
                port=80,
                target_port="http",
            )
        ],
        selector={
            "appClass": "my-deployment",
        },
    ),
    opts=pulumi.ResourceOptions(provider=cluster_provider),
)

# Export the URL for the load balanced service.
pulumi.export("svc-url", my_service.status.load_balancer.ingress[0].hostname)
