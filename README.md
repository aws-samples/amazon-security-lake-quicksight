## Table of Contents
1. [About this Repo](#About)
2. [Usage Guide](#Usage)
3. [Examples](#Examples)
4. [License](#License)

## About this Repo <a name="About"></a>

This repository a combinatination of CDK tools and scripts which can be used to create the required AWS objects and deploy basic datasources, datasets, analysies, dashboards, and user groups to Quicksight with respect to Amazon Security Lake.

We welcome contributions to this repo in the form of fixes to existing examples or addition of new examples. For more information on contributing, please see the [CONTRIBUTING](https://github.com/aws-samples/amazon-security-lake/blob/main/CONTRIBUTING.md) guide.


## Solution Overview <a name="Solution Overview"></a>

![Solution Overview](/amazon-security-lake-quicksight/security_lake_quicksight_deployment_architecture.jpg)

## Usage Guide <a name="Usage"></a>

cdk-lakeformation-permissions/source/cdk.json
  
	{
  		"app": "python3 app.py",
  		"context": {
			"rollup_region": "ROLLUPREGION",
			"region": "QSREGION",
			"slregion": "SLREGION",
			"LakeFormationAdminRoleARN": "arn:aws:iam::ACCOUNTID:role/ROLENAME",
			"SecurityLakeAccountID": SECURITYLAKEACCOUNTID,
			"QuickSightUserARN": "QUICKSIGHTUSERARN"
   	 	}
  	}
	
  
cdk-lakeformation-permissions/source/runCommands.sh

	echo "--------------------------------"
	echo "Running cdk deploy --all command"
	echo "--------------------------------"
	cdk deploy --all -v --debug
	echo "--------------------------------"
	echo "Finished cdk deploy"
	echo "--------------------------------"
	python3 ../../qs_lake_generate.py --account ACCOUNTID  --principal QUICKSIGHTUSERARN --region QSREGION --slregion SLREGION

in the source dir run:

	cdk synth
	./runCommand.sh

## Examples <a name="Examples"></a>

cdk-lakeformation-permissions/source/cdk.json
  
	{
  		"app": "python3 app.py",
  		"context": {
			"rollup_region": "us_east_1",
			"region": "us-east-1",
			"slregion": "us-east-1",
			"LakeFormationAdminRoleARN": "arn:aws:iam::ACCOUNTID:role/example-role",
			"SecurityLakeAccountID": 1111222233334444,
			"QuickSightUserARN": "arn:aws:quicksight:us-east-1:1111222233334444:user/default/Admin/example-role"
   	 	}
  	}
  
cdk-lakeformation-permissions/source/runCommands.sh

	echo "--------------------------------"
	echo "Running cdk deploy --all command"
	echo "--------------------------------"
	cdk deploy --all -v --debug
	echo "--------------------------------"
	echo "Finished cdk deploy"
	echo "--------------------------------"
	python3 ../../qs_lake_generate.py --account ACCOUNTID  --principal QUICKSIGHTUSERARN --region us-east-1 --slregion us-east-1

in the source dir run:

	cdk synth
	./runCommand.sh


### Official Resources
- [Amazon Security Lake Overview](https://aws.amazon.com/security-lake/)
- [Amazon Quicksight Overview](https://aws.amazon.com/quicksight/)

# License <a name="License"></a>

This library is licensed under the MIT-0 License.
