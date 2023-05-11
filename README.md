Amazon Security Lake Data Validation 
========================

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
	    "rollup_region": "<region>",
	    "region": "<region>",
	    "slregion": "<region>",
	    "LakeFormationAdminRoleARN": "arn:aws:iam::123456789012:role/<Rolename>",
	    "SecurityLakeAccountID": 123456789012,
	    "AWSAccountID":555555555555,
	    "QuickSightUserARN": "arn:aws:quicksight:<Region>:123456789012:user/default/<PrincipalId>"   
	  }
	}
	
  
scripts/qsdeploy.sh

	#!/bin/bash
	#parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
	cd "$parent_path/source"

	echo "Running cdk deploy --all command"
	echo "--------------------------------------------"
	echo " "
	cdk deploy --all -v
	echo "Finished cdk deploy"
	echo "--------------------------------------------"

	echo "Running QuickSight Generate Dashboards"
	echo "--------------------------------------------"
	echo " "
	python3 createobjects.py
	echo "Finished QuickSight Generate Dashboards"
	echo "--------------------------------------------"


## Examples <a name="Examples"></a>

cdk-lakeformation-permissions/source/cdk.json
  
	{
	  "app": "python3 app.py",
	  "context": {
	    "rollup_region": "<region>",
	    "region": "<region>",
	    "slregion": "<region>",
	    "LakeFormationAdminRoleARN": "arn:aws:iam::123456789012:role/<Rolename>",
	    "SecurityLakeAccountID": 123456789012,
	    "AWSAccountID":555555555555,
	    "QuickSightUserARN": "arn:aws:quicksight:<Region>:123456789012:user/default/<PrincipalId>"   
	  }
	}
  
scripts/qsdeploy.sh

	#!/bin/bash
	#parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
	cd "$parent_path/source"

	echo "Running cdk deploy --all command"
	echo "--------------------------------------------"
	echo " "
	cdk deploy --all -v
	echo "Finished cdk deploy"
	echo "--------------------------------------------"

	echo "Running QuickSight Generate Dashboards"
	echo "--------------------------------------------"
	echo " "
	python3 createobjects.py
	echo "Finished QuickSight Generate Dashboards"
	echo "--------------------------------------------"


### Official Resources
- [Amazon Security Lake Overview](https://aws.amazon.com/security-lake/)
- [Amazon Quicksight Overview](https://aws.amazon.com/quicksight/)

# License <a name="License"></a>

This library is licensed under the MIT-0 License.
