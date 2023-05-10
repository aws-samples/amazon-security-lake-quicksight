from constructs import Construct
import aws_cdk as cdk

from aws_cdk import (
    Aws,
    Stack,
    CfnOutput,
    aws_lakeformation as lf,
)

class CdkDbStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Retrieve the AWS account ID
        account_id = Aws.ACCOUNT_ID
        
        # Retrieve the principal ID of the AWS user or role that is creating the stack
        #principal_id = Aws.PRINCIPAL_ID
        
        lake_formation_admin_role_arn = cdk.CfnParameter(
            self,
            "LakeFormationAdminRoleARN",
            type="String",
            description="Enter ARN of your LakeFormation Admin.",
            default=self.node.try_get_context('LakeFormationAdminRoleARN')
        )

        security_lake_account_id = cdk.CfnParameter(
            self,
            "SecurityLakeAccountID",
            type="String",
            description="Enter Security Lake AccountID.",
            default=self.node.try_get_context('SecurityLakeAccountID')
        )

        quicksight_user_arn = cdk.CfnParameter(
            self,
            "QuickSightUserARN",
            type="String",
            description="Enter ARN of your Quicksight User. for example: arn:aws:quicksight:<region>:<aws_account_id>:user/default/admin/<federated user>",
            default=self.node.try_get_context('QuickSightUserARN')
        )

        # Define Lake Formation Admin Permissions
        cfn_data_lake_settings = lf.CfnDataLakeSettings (
            self,
            "LakeFormationAdminPermissions",
            admins=[lf.CfnDataLakeSettings.DataLakePrincipalProperty(
                data_lake_principal_identifier=lake_formation_admin_role_arn.value_as_string
            )],
            trusted_resource_owners=[
                self.account,
                security_lake_account_id.value_as_string
            ]
        )

        self.security_lake_account_id = security_lake_account_id
        self.quicksight_user_arn = quicksight_user_arn


        #CfnOutput(self, "account", value=security_lake_account_id.value_as_string)