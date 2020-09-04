import { expect as expectCDK, matchTemplate, MatchStyle } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import { nlb_stack,ga_stack } from '../lib/hls-proxy-stack';


test('Empty Stack', () => {
    const app = new cdk.App();


     
    // WHEN
    const my_nlb_fargate = new nlb_stack(app, 'HlsProxyStack').nlb_fargate;
    new ga_stack(app,'my-ga-stack',my_nlb_fargate)
        // THEN
    expectCDK(ga_stack).to(matchTemplate({
      "Resources": {}
    }, MatchStyle.EXACT))
});
