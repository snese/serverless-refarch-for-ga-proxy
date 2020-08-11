from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_ecs_patterns as ecs_patterns,
    core,
    aws_elasticloadbalancingv2 as elbv2,
    aws_globalaccelerator as globalaccelerator
)


class BonjourFargate(core.Stack):

    def __init__(self, scope: core.Construct, id , **kwargs) -> None:
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
        
        repo_ = ecr.Repository.from_repository_arn(self, id = 'hls-proxy', repository_arn='arn:aws:ecr:us-east-1:927529796467:repository/hls-proxy')
        
        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self, "FargateService",
            cluster=cluster,
            task_image_options={
                'image': ecs.ContainerImage.from_ecr_repository(repository=repo_)
            }
        )

        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(80),
            description="Allow http inbound from VPC"
        )
        

        accelerator = globalaccelerator.Accelerator(self, "Accelerator")
        listener1 = globalaccelerator.Listener(self, "Listener",accelerator = accelerator, port_ranges = [{"from_Port": 80,"to_Port": 80}])
        
        endpoint_group = accelerator.EndpointGroup(self, "Group", listener=listener1)
        endpoint_group.add_load_balancer("NlbEndpoint", fargate_service.load_balancer)

        core.CfnOutput(
            self, "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name
        )
        

app = core.App()

BonjourFargate(app, "Bonjour",env = core.Environment(account= '927529796467', region='ap-east-1'))
app.synth()
