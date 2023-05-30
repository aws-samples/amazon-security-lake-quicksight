## Table of Contents
1. [About this Repo](#About)
2. [Usage Guide](#Usage)
3. [Examples](#Examples)
4. [Cost & Performance](#Cost&Performance)
5. [Dashboard Customization](#DashboardCustomization)
6. [License](#License)

## About this Repo <a name="About"></a>

This repository a combinatination of CDK tools and scripts which can be used to create the required AWS objects and deploy basic datasources, datasets, analysies, dashboards, and user groups to Quicksight with respect to Amazon Security Lake.

We welcome contributions to this repo in the form of fixes to existing examples or addition of new examples. For more information on contributing, please see the [CONTRIBUTING](https://github.com/aws-samples/amazon-security-lake/blob/main/CONTRIBUTING.md) guide.

## Prerequisites <a name="Prerequisites"></a>
* Enable Amazon Security Lake. For multiple AWS accounts, it is recommended to manage Security Lake for AWS Organizations To help automate and streamline the management of multiple accounts, we strongly recommend that you integrate Security Lake with AWS Organizations.

* As part of this solution, you will need to enable Amazon QuickSight and configure users and groups. Here is the link (https://docs.aws.amazon.com/quicksight/latest/user/creating-quicksight-groups.html) for creating and managing groups in Amazon QuickSight. 

* Install the latest release of the AWS CLI version 2: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

## Solution Overview <a name="Solution Overview"></a>

![Solution Overview](/images/security_lake_quicksight_deployment_architecture.jpg)

## Usage Guide <a name="Usage"></a>

Edit cdk-lakeformation-permissions/source/cdk.json using the values for your specific Amazon Security Lake and Amazon Quicksight Instance:

1. rollup_region - 
2. region - 
3. slregion - 
4. LakeFormationAdminRoleArn - 
5. SecurityLakeAccountID - 
6. AWSAccountID - 
7. QuicksightUserARN - 


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


To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .env
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .env/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .env\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

Set environment variables or Specifies the name of the AWS CLI profile with the credentials and options to use.

```
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_DEFAULT_REGION=us-east-1
```

At this point you can run script to synthesize the CloudFormation template and deploy AWS Lake Formation permissions and QuickSight dashboards.

```
$ qsdeploy.sh
```

## Examples <a name="Examples"></a>

Edit cdk-lakeformation-permissions/source/cdk.json using the values for your specific Amazon Security Lake and Amazon Quicksight Instance:

1. rollup_region - 
2. region - 
3. slregion - 
4. LakeFormationAdminRoleArn - 
5. SecurityLakeAccountID - 
6. AWSAccountID - 
7. QuicksightUserARN - 
	
	
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
  
Run 

	qsdeploy.sh
	
	
![Solution Overview](/images/analyst.png)

![Solution Overview](/imagescustodian.png)

![Solution Overview](/images/executive.png)

### Official Resources
- [Amazon Security Lake Overview](https://aws.amazon.com/security-lake/)
- [Amazon Quicksight Overview](https://aws.amazon.com/quicksight/)

# License <a name="License"></a>

This library is licensed under the MIT-0 License.
