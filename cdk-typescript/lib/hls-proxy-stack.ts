import ec2 = require('@aws-cdk/aws-ec2');
import ecs = require('@aws-cdk/aws-ecs');
import ecs_patterns = require('@aws-cdk/aws-ecs-patterns');
import cdk = require('@aws-cdk/core');
import globalaccelerator = require('@aws-cdk/aws-globalaccelerator');
import { TLSSocket } from 'tls';
import { Port } from '@aws-cdk/aws-ec2';
import path = require('path')



export class nlb_stack extends cdk.Stack {
  
  public nlb_fargate: ecs_patterns.NetworkLoadBalancedFargateService ;
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create VPC and Fargate Cluster
    // NOTE: Limit AZs to avoid reaching resource quotas
    const vpc = new ec2.Vpc(this, 'MyVpc', { maxAzs: 3 });
    const cluster = new ecs.Cluster(this, 'Cluster', { vpc });

    // Instantiate Fargate Service with just cluster and image
      this.nlb_fargate = new ecs_patterns.NetworkLoadBalancedFargateService(this, "FargateService", {
      cluster,
      publicLoadBalancer: false,
      taskImageOptions: {
        image: ecs.ContainerImage.fromAsset(path.resolve('./', 'docker_folder'))      
      },
    });


    const listener = this.nlb_fargate.loadBalancer.addListener('Listener', {
      port: 443,
    });

    listener.addTargets("serviceName", {
        port: 80,
        targets: [this.nlb_fargate.service],
    });
    
    this.nlb_fargate.service.connections.securityGroups[0].addIngressRule(
      ec2.Peer.ipv4(vpc.vpcCidrBlock),
      ec2.Port.tcp(80)
    )
  

    const scaling = this.nlb_fargate.service.autoScaleTaskCount({ maxCapacity: 2 });
    
    scaling.scaleOnCpuUtilization('CpuScaling', {
      targetUtilizationPercent: 70,
      scaleInCooldown: cdk.Duration.seconds(60),
      scaleOutCooldown: cdk.Duration.seconds(60)
    });


  }
} 



export class ga_stack extends cdk.Stack {
  
  constructor(scope: cdk.App, id: string, nlb: ecs_patterns.NetworkLoadBalancedFargateService ,props?: cdk.StackProps) {
    super(scope, id, props);
    const accelerator = new globalaccelerator.Accelerator(this,"Accelerator")
    const my_listener = new globalaccelerator.Listener(this, 'Listener', {
      accelerator,
      portRanges: [
        {
          fromPort: 80,
          toPort: 80,
        },
        {
          fromPort: 443,
          toPort: 443,
        },
      ],
    });
    const endpoint_group = new globalaccelerator.EndpointGroup(this,"Group", {listener:my_listener})
    endpoint_group.addLoadBalancer("NlbEndpoint", nlb.loadBalancer)
  }
}