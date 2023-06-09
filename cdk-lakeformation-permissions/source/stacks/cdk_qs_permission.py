from constructs import Construct
import aws_cdk as cdk
import os
from aws_cdk import (
    Stack,
    aws_glue as glue,
    aws_lakeformation as lf,
    aws_quicksight as qs,
    Aws
)


class CdkPermissionStack(Stack):
    def __init__(self, scope: Construct, id: str, security_lake_account_id, quicksight_user_arn, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        tables = ['cloud_trail_mgmt_1_0', 'route53_1_0', 'sh_findings_1_0', 'vpc_flow_1_0']
        permission_list = {
                     "qs_arn":quicksight_user_arn.value_as_string,
                     "operator":f"arn:aws:quicksight:{Stack.of(self).region}:{Stack.of(self).account}:group/default/security-lake-operator-group",
                     "custodian":f"arn:aws:quicksight:{Stack.of(self).region}:{Stack.of(self).account}:group/default/security-lake-custodian-group",
                     "executive":f"arn:aws:quicksight:{Stack.of(self).region}:{Stack.of(self).account}:group/default/security-lake-executive-group"

                 }

        rollup_region = self.node.try_get_context('rollup_region')
        AWSAccountID = int(os.getenv('CDK_DEFAULT_ACCOUNT'))
        SecurityLakeAccountID= int(self.node.try_get_context('SecurityLakeAccountID'))
        data_lake_admin_id = self.node.try_get_context(
            'LakeFormationAdminRoleARN')

        admin_permissions = lf.CfnDataLakeSettings(
            self, "DataLakeSettings",
            admins=[
                lf.CfnDataLakeSettings.DataLakePrincipalProperty(
                    data_lake_principal_identifier=f"arn:aws:iam::{Stack.of(self).account}:role/cdk-hnb659fds-cfn-exec-role-{Stack.of(self).account}-{Stack.of(self).region}"),
                lf.CfnDataLakeSettings.DataLakePrincipalProperty(
                    data_lake_principal_identifier=data_lake_admin_id)])

        if AWSAccountID != SecurityLakeAccountID:
            security_lake_resource_link = glue.CfnDatabase(self, "SecurityLakeResourceLink",
                                                        catalog_id=self.account,
                                                        database_input=glue.CfnDatabase.DatabaseInputProperty(
                                                            name=f"amazon_security_lake_glue_db_{rollup_region}",
                                                            target_database=glue.CfnDatabase.DatabaseIdentifierProperty(
                                                                catalog_id=security_lake_account_id.value_as_string,
                                                                database_name=f"amazon_security_lake_glue_db_{rollup_region}"
                                                            )
                                                        ))

        for key, value in permission_list.items(): 
            describe_permissions = lf.CfnPrincipalPermissions(self, "QSTablePermissionsDatabase"+key,
                                                permissions=["DESCRIBE"],
                                                permissions_with_grant_option=[],
                                                principal=lf.CfnPrincipalPermissions.DataLakePrincipalProperty(
                                                    data_lake_principal_identifier=value,
                                                ),
                                                resource=lf.CfnPrincipalPermissions.ResourceProperty(
                                                    database=lf.CfnPrincipalPermissions.DatabaseResourceProperty(
                                                        catalog_id=self.account,
                                                        name=f"amazon_security_lake_glue_db_{rollup_region}"
                                                    )
                                                ))
            if AWSAccountID != SecurityLakeAccountID:
                describe_permissions.add_dependency(security_lake_resource_link)
            else:
                describe_permissions.add_dependency(admin_permissions)

            for table in tables:
                # Define the LakeFormation principal permissions
                table_permissions = lf.CfnPrincipalPermissions(self, f"{table.capitalize()}QSTablePermissions"+key,
                                        permissions=["SELECT"],
                                        permissions_with_grant_option=[],
                                        principal=lf.CfnPrincipalPermissions.DataLakePrincipalProperty(
                                            data_lake_principal_identifier=value,
                                        ),
                                        resource=lf.CfnPrincipalPermissions.ResourceProperty(
                                            table=lf.CfnPrincipalPermissions.TableResourceProperty(
                                                catalog_id=security_lake_account_id.value_as_string,
                                                database_name=f"amazon_security_lake_glue_db_{rollup_region}",
                                                name=f"amazon_security_lake_table_{rollup_region}_{table}"
                                            )
                                        ))
                table_permissions.add_dependency(describe_permissions)
