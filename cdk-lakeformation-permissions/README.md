
# Welcome to your CDK Python project!

## Pre requisite:
 * In Amazon Security Lake 
 * Setup Security Lake in an account (Source account)
 * Sets up procedures to populate the S3 buckets with service-based information
 * Uses Lake Formation to create
 *	amazon_security_lake_glue_db_<<region>> - database
 * amazon_security_lake_table_<<region>><<service>> -- tables
 *	maps the tables to S3 created above
 *	provides grants to <<admin group>> to access the database and tables
 *	The database and tables are visible from glue (hence Athena)
 *	Not down the Account Number (SRC_AccountNum)

 * In QuickSight 
 * If not existing setup Quicksight account (VIZ_ AccountNum) (Can be different from Source account)
 * In Cloud9	
 * aws quicksight list-users --aws-account-id < VIZ_ AccountNum > --namespace default will give the arn of the user(VIZ_user_arn)



This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!