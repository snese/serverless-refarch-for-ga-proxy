# AWS Serverless Reference Architecture for AWS Global Accelerator with Reverse Proxy
![Reference Architecture](Architecture.jpg)

Amazon Interactive Video Service (https://aws.amazon.com/ivs/) (Amazon IVS) is a managed live streaming solution that is quick and easy to set up, and ideal for creating interactive video experiences. It provides ultra low latency (< 5s) service for video streaming.

Currently, Amazon IVS is not supported in some regions. We implement a serverless solution to serve the user in unsupported regions. AWS Fargate with auto scaling group and Network Load Balancer are used to host a reverse proxy to for IVS playback URL. AWS global accelerator is used to reduce network latency. 

To achieve the ultra low latency, the Amazon IVS player and HTTPS playback URL is required, Amazon Route 53 is used to route traffic to NLB with TLS certificate provided by AWS Certificate Manager.


# Why Reverse Proxy on AWS Fargate
AWS Fargate is a serverless compute service that helps container orchestration services such as Amazon ECS to provision containers without managing any EC2 instances. This repo aims to run Reverse Proxy in a serverless environment as a middle stack between AWS Global Accelerator and the endpoints you want to pass through the proxy.

# Benefits for AWS Global Accelerator
TBW

# How to deploy
### Prerequisites

#### [Install AWS CLI and set up your own configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)

#### Set up CDK Enviorment: 
```

# 1. Install CDK Toolkit
npm install -g aws-cdk

# 2. Clone the Repository
git clone https://github.com/snese/serverless-refarch-for-ga-proxy

# 3. Install required modules
cd serverless-refarch-for-ga-proxy
npm install

# 4. Bootstrapping an environment (If it is your first time to deploy AWS CDK App in the Region)
cdk bootstrap


```
#### Deployment:  

```
# Estimated deployment time: 5 min

# 1. Create a custom configuration of Nginx 
node ./lib/create-conf.js <your-proxy-url>


# 2. Deploy your CDK App
cdk deploy "*"

```

# License Summary
This library is licensed under the MIT-0 License. See the LICENSE file.
