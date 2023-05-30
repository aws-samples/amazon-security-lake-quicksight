#!/usr/bin/env python3

from aws_cdk import App

from stacks.cdk_external_db import CdkDbStack
from stacks.cdk_qs_permission import CdkPermissionStack

app = App()

external_db_stack           = CdkDbStack(app, "cdk-db")
qs_permission_stack         = CdkPermissionStack(app, "cdk-permission", 
                                                 security_lake_account_id=external_db_stack.security_lake_account_id,
                                                 quicksight_user_arn=external_db_stack.quicksight_user_arn)
app.synth()