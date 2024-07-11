# Infrastructure as Code (Pulumi)

## Setup

Download pulumi

```
brew install pulumi
```

Login to Pulumi Cloud using our shared account and create an access token

1. Sign into pulumi.com using the creds found in 1Pasword (mlrunner@mozilla.ai)

2. Go to the [Personal access tokens](https://app.pulumi.com/mzai-mlrunner/settings/tokens)
 page to create a new personal access token for yourself

3. Run the following command to login

```
pulumi login
```

And enter your personal access token when prompted.

## AWS Credentials
Download AWS CLI

Sandbox root account creds in 1Password

Create IAM account in AWS sandbox account?

Create an Access key and put in .env file


## Kube Access


## Project Layout

There are two main pulumi stacks in this folder:

`Infra` - This stack is the baseline infra needed for the lumigator

`App` - This stack is the app itself, it can be run every time a new code version is deployed.


# Running Pulumi

```
env $(cat .env | xargs) pulumi up
```

# Best Practices

DependsOn / Resource Graph

```
opts=pulumi.ResourceOptions(depends_on=[cluster])
```

https://www.pulumi.com/docs/concepts/inputs-outputs/all/

# Troubleshooting

Sometimes it's easier to apply and `UP` to delete a resource

State manipulation

"Stuck" Resources

opts=pulumi.ResourceOptions(depends_on=[cluster])

Auth tokens, etc timing out after x minutes

Failed up and destroy

Token error

Run both and up and destroy to test that resources created and destroyed correctly.

# EKS ENI issue
https://github.com/pulumi/pulumi-eks/issues/382

When destroying EKS clusters, there seems to be an issue with destroying dependent ENIs

```
DependencyViolation: resource sg-0bf103c05a6fd8766 has a dependent object
```

You can see dependent objects for the security group using the following command:

```
aws ec2 describe-network-interfaces --filters Name=group-id,Values=sg-0bf103c05a6fd8766
```
