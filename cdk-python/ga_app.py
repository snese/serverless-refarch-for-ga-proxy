from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_globalaccelerator as globalaccelerator,
    core,
)
import os
import click
from aws_cdk.aws_ecr_assets import DockerImageAsset
import docker




class nlb_fargate_stack(core.Stack):

    def __init__(self, scope: core.Construct, id: str,**kwargs) -> None:
        super().__init__(scope, id,**kwargs)

        # Create VPC and Fargate Cluster
        # NOTE: Limit AZs to avoid reaching resource quotas
        vpc = ec2.Vpc(
            self, "MyVpc",
            max_azs = 3 
        )

        cluster = ecs.Cluster(
            self, 'Ec2Cluster',
            vpc=vpc
        )
        
        
        #asset = DockerImageAsset(self, "MyBuildImage",directory = os.path.join("docker_folder", "my-image"))
        
        self.fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self, "FargateService",
            cluster=cluster,
            public_load_balancer = True,
            task_image_options={
                'image': ecs.ContainerImage.from_registry("hhh2012aa/hls-nginx")
            }
        )
        

        self.fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(80),
            description="Allow http inbound from VPC"
        )
        
        scaling = self.fargate_service.service.auto_scale_task_count(
            max_capacity = 2
        )
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=70,
            scale_in_cooldown=core.Duration.seconds(60),
            scale_out_cooldown=core.Duration.seconds(60),
        )
        
        #self.fargate_service.load_balancer.add_listener('listener', port = 443)
        self.fargate_service.listener.port = 443
        self.fargate_service.listener.certificates = ""
        print()
        
class ga_stack(core.Stack):
    def __init__(self, scope: core.Construct, id: str,**kwargs) -> None:
        
        super().__init__(scope, id,**kwargs)
        
        my_nlb_fargate = nlb_fargate_stack(app, "hls-default", env= my_env)
        accelerator = globalaccelerator.Accelerator(self, "Accelerator")
        my_listener = globalaccelerator.Listener(self, "Listener",accelerator = accelerator, 
        port_ranges = [{"fromPort": 80,"toPort": 80},{"fromPort": 443,"toPort": 443}])
        
        endpoint_group = globalaccelerator.EndpointGroup(self, "Group", listener=my_listener)
        endpoint_group.add_load_balancer("NlbEndpoint", my_nlb_fargate.fargate_service.load_balancer)


        core.CfnOutput(
            self, "LoadBalancerDNS",
            value=accelerator.dns_name
        ) 


def create_conf(ivsurl):
    f = open("nginx.conf", "w+")
    f.write(
    """
    events {
      worker_connections  1024;
    }
    
    http{
      default_type application/octet-stream;
      server {
        listen 80;
        server_name localhost;
        location  / {
          proxy_pass %s;
         }
    }
        types {
          application/vnd.apple.mpegurl m3u8;
        }
    }
    """
    % (ivsurl))
    
    client = docker.from_env()
    client.login(username = <yourid>, password = <yourpassword>)
    client.images.build(path = "./docker_folder",tag = "<yourid>/hls-nginx") 
    client.images.push('<yourid>/hls-nginx')



if __name__ == '__main__':
    
    app = core.App()
    
    IVSURL = app.node.try_get_context("IVSURL")
    create_conf(IVSURL)

    my_env = core.Environment(
        account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
        region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]))
        
    
    my_ga = ga_stack(app, "ga-default", env= my_env) 
    app.synth()
