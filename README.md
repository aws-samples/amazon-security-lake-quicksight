## Table of Contents
1. [About this Repo](#About)
2. [Usage Guide](#Usage)
3. [Examples](#Examples)
4. [Cost & Performance](#Cost&Performance)
5. [Dashboard Customization](#DashboardCustomization)
6. [License](#License)

## About this Repo <a name="About"></a>

NOTE: This is a sample, non-production-ready template.

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

1. rollup_region - The aggregate region used for rollup in Amazon Security Lake. This field require the use of an underscore rather than dash (example: us_east_1 rather than us-east-1).
2. region - The current region where this solution is being deployed to.
3. slregion - The region where the referenced Security Lake tables reside. 
4. LakeFormationAdminRoleArn - The Admin Role ARN used in AWS Lake Formation.
5. SecurityLakeAccountID - The AWS Account ID which has provided the resource share to its security lake assets.
6. AWSAccountID - The AWS Account ID from which you are deploying the Quicksight solution to.  Depending on your set up, it may or may not be the same as the SecurityLakeAccountID.
7. QuicksightUserARN - The AWS Quicksight ARN of the Quicksight account in which this solution is being deployed to.


		{
		  "app": "python3 app.py",
		  "context": {
		    "rollup_region": "<region>",
		    "region": "<region>",
		    "slregion": "<region>",
		    "LakeFormationAdminRoleARN": "arn:aws:iam::123456789012:role/<Rolename>",
		    "SecurityLakeAccountID": "123456789012",
                    "AWSAccountID": "123456789012",
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
	
		{
		  "app": "python3 app.py",
		  "context": {
		    "rollup_region": "<region>",
		    "region": "<region>",
		    "slregion": "<region>",
		    "LakeFormationAdminRoleARN": "arn:aws:iam::123456789012:role/<Rolename>",
		    "SecurityLakeAccountID": 123456789012,
		    "QuickSightUserARN": "arn:aws:quicksight:<Region>:123456789012:user/default/<PrincipalId>"   
		  }
		}
  
Run 

	qsdeploy.sh
	

Add QuickSight Users to the appropriate Dashboard groups
* Within QuickSight, select your user profile (top-right icon)
* Select Manage QuickSight, and then Manage Groups
* Select the appropriate group (security-lake-executive-group, security-lake-operator-group, security-lake-custodian-group)
* Select Add user, and add a user to the group.
* You will have to do this for each Dashboard as needed.

Once users are added into the appropriate group(s), the user will have access to the Dashboard(s)

![Solution Overview](/images/analyst.png)

![Solution Overview](/images/custodian.png)

![Solution Overview](/images/executive.png)

## Quicksight Cost <a name="Cost&Performance"></a>

Please refer to the following on Amazon Quicksight cost: https://aws.amazon.com/quicksight/pricing/.

## Dashboard Customization <a name="#DashboardCustomization"></a>

This solution has been designed as a generally available solution for users who wish to visualize their Amazon Security Lake data. For users with specific visualization needs, the quicksight analysis has been provided in addition to the dashboards. In Amazon QuickSight, an analysis is the same thing as a dashboard, except that it can only be accessed by the authors you choose. You can keep it private, and  When and if you decide to publish it, the it can be edited to add or remove visuals before being shared as a new dashboard.For more information on how to customize the analysis provided by this solution, please refer to the following: https://docs.aws.amazon.com/quicksight/latest/user/working-with-an-analysis.html.

### Official Resources
- [Amazon Security Lake Overview](https://aws.amazon.com/security-lake/)
- [Amazon Quicksight Overview](https://aws.amazon.com/quicksight/)

# License <a name="License"></a>

This library is licensed under the MIT-0 License.
