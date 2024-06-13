import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx

BACKEND_REPOSITORY_URL = "backend-repo-url"
JOB_RUNNER_REPOSITORY_URL = "jobrunner-repo-url"

repo = aws.ecr.Repository(
    "backend-repo-new", opts=pulumi.ResourceOptions(import_="backend-repo-f0dd567")
)

# backend_repository = awsx.ecr.Repository(
#    "backend-repo",
#    awsx.ecr.RepositoryArgs(force_delete=True),
#    opts=pulumi.ResourceOptions(import_="backend-repo-f0dd567"),
# )
#
# pulumi.export(BACKEND_REPOSITORY_URL, backend_repository.url)

# jobrunner_repository = awsx.ecr.Repository(
#    "job-runner-repo",
#    awsx.ecr.RepositoryArgs(force_delete=True),
# )
#
# pulumi.export(JOB_RUNNER_REPOSITORY_URL, backend_repository.url)
