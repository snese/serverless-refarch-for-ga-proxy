
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    core,
)


class BonjourFargate(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create VPC and Fargate Cluster
        # NOTE: Limit AZs to avoid reaching resource quotas
        vpc = ec2.Vpc.from_lookup(
            self, 'vpc',
            vpc_id='vpc-67a9460e'
        )

        cluster = ecs.Cluster(
            self, 'Ec2Cluster',
            vpc=vpc
        )

        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self, "FargateService",
            cpu = 256, memory_limit_mib = 1024,
            task_image_options={
                'image': ecs.ContainerImage.from_asset("../docker_folder")
            }
        )

        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(80),
            description="Allow http inbound from VPC"
        )

        core.CfnOutput(
            self, "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name
        )

app = core.App()
BonjourFargate(app, "Bonjour-local",env = core.Environment(account= '927529796467', region='ap-east-1'))
app.synth()
