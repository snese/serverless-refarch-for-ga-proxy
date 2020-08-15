from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_globalaccelerator as globalaccelerator,
    core,
)
import os


class nlb_fargate_stack(core.Stack):

    def __init__(self, scope: core.Construct, id: str,**kwargs) -> None:
        super().__init__(scope, id,**kwargs)

        # Create VPC and Fargate Cluster
        # NOTE: Limit AZs to avoid reaching resource quotas
        vpc = ec2.Vpc(
            self, "MyVpc",
            max_azs=2
        )

        cluster = ecs.Cluster(
            self, 'Ec2Cluster',
            vpc=vpc
        )

        self.fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self, "FargateService",
            cluster=cluster,
            public_load_balancer = True,
            task_image_options={
                'image': ecs.ContainerImage.from_asset("../docker_folder")
            }
        )

        self.fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(80),
            description="Allow http inbound from VPC"
        )
        
class ga_stack(core.Stack):
    def __init__(self, scope: core.Construct, id: str,**kwargs) -> None:
        
        super().__init__(scope, id,**kwargs)
        accelerator = globalaccelerator.Accelerator(self, "Accelerator")
        listener1 = globalaccelerator.Listener(self, "Listener",accelerator = accelerator, port_ranges = [{"fromPort": 80,"toPort": 80}])
        
        endpoint_group = globalaccelerator.EndpointGroup(self, "Group", listener=listener1)
        endpoint_group.add_load_balancer("NlbEndpoint", my_nlb_fargate.fargate_service.load_balancer)


        core.CfnOutput(
            self, "LoadBalancerDNS",
            value=accelerator.dns_name
        ) 

app = core.App()
my_env = core.Environment(
    account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
    region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]))
    
my_nlb_fargate = nlb_fargate_stack(app, "hls-default", env= my_env)
my_ga = ga_stack(app, "ga-default", env= my_env)


app.synth()
