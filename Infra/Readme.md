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

`Infra` - This stack is the baseline infra needed for the platform

`App` - This stack is the app itself, it can be run every time a new code version is deployed.



