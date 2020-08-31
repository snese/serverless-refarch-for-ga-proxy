#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { nlb_stack,ga_stack } from '../lib/hls_proxy-stack';

const app = new cdk.App();
const my_nlb_fargate = new nlb_stack(app, 'HlsProxyStack').nlb_fargate;
new ga_stack(app,'my-ga-stack',my_nlb_fargate)
