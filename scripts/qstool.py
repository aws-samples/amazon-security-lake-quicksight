#!/usr/bin/python3
#
# Amazon Quicksight Asset Bundling and Deployment Tool (aqsabdt)
#
# [nbb@20230310] PoC via Makefile
# [nbb@20230413] PoC Python implementation
# [nbb@20230420] Publish to repository
#
# Recently Done:
# - Basic group support for permissions across all asset types
#
# Todo - Remaining
# - Support for more than Athena and CustomSql - just need to test .. no use cases
# - Promote/demote analysis to/from dashboard
# ! Fix prefix/suffix
# - Dashboard versioning (opportunity)
#   - Support for embedded widget with dynamic versioning for visuals .. interesting thought
# ! Better exception handling

import json
from json import JSONEncoder
import datetime
import argparse
import boto3
import re

# some default for testing
DEF_ASSETS = 'assets.json'
DEF_CATALOG = 'catalog.json'
DEF_OUTPUT = 'output.json'

# parse command line directives and options
cliparser = argparse.ArgumentParser( description="Amazon Quicksight Asset Deployment Tool")
cliparser.add_argument('action', choices=['list', 'describe', 'sanitize', 'create','update','delete'], help="Action to execute")
cliparser.add_argument('type', choices=['all','dashboard','analysis','dataset','datasource','group'], help="Type of asset")
cliparser.add_argument('ids', nargs='*', help="Asset IDs")
cliparser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose orchestration output")
cliparser.add_argument('-f', '--nofollow', action='store_true', help="Do NOT follow any dependency objects")
cliparser.add_argument('-C', '--confirm', action='store_true', help="Confirmation for destructive actions")
cliparser.add_argument('-p', '--preopen', action='store_true', help="Preopen assets file for merging additional assets")
cliparser.add_argument('-i', '--ignore', action='store_true', help="Ignore errors when assets already exist or do not exist")
cliparser.add_argument('--account', help="Amazon account ID")           # used for api calls and sanitize
cliparser.add_argument('--region', help="Amazon account region")        # used for sanitize
cliparser.add_argument('--slregion', help="Amazon Security Lake region")     # used for Amazon Security Lake
cliparser.add_argument('--asl', help="(deprecated) Amazon Security Lake region")     # used for Amazon Security Lake
cliparser.add_argument('--assets', default=DEF_ASSETS, help=f"Asset definitions file for export/deploy ({DEF_ASSETS})")
cliparser.add_argument('--catalog', default=DEF_CATALOG, help=f"Filename to write API output/results for list/delete ({DEF_CATALOG})")
cliparser.add_argument('--output', default=DEF_OUTPUT, help=f"Filename to write API output/results for list/delete ({DEF_OUTPUT})")
cliparser.add_argument('--principal', default='', help="Principal to apply permissions to assets")
cliparser.add_argument('--prefix', default='', help="Prefix string to front Names and Ids")
cliparser.add_argument('--suffix', default='', help="Suffix string to trail Names and Ids")
args = cliparser.parse_args()

# for collecting debug and API results
results = []

# instrumentation
def debug(x, y = 0):
    if args.verbose or y == 255:
        print(x)
    results.append(x)
    if y == 0: return
    print("!! access the help menu with -h or --help")
    #cliparser.print_help()
    exit(255)

# holding space for collection of assets
assets = {
    "namespaces": {},
    "dashboards": {},
    "analyses": {},
    "templates": {},
    "datasets": {},
    "datasources": {},
    "groups": {}
}

# sanitize prefix/suffix - spaces/tabs/slashes to -
args.prefix = re.sub(r'([\s\t/]+)', '-', args.prefix)
args.suffix = re.sub(r'([\s\t/]+)', '-', args.suffix)

if args.prefix or args.suffix:
    debug('!! --prefix and --suffix are only partially implemented and are not ready for use yet', 255)

# attempt to get the account id if not supplied - not needed for sanitize
if not args.account and args.action not in ['sanitize']:
    debug("getting account info via sts.get_caller_identity")
    try:
        sts = boto3.client('sts')
        args.account = sts.get_caller_identity()['Account']
        sts.close()
    except Exception as e:
        debug("!! cannot call sts:get_caller_identity", 255)

# open up client connection to Amazon Quicksight
debug("opening Amazon Quicksight connection")
qs = boto3.client('quicksight')

###
## Helper functions
###

# json encoder for datetime object
class DateTimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


# encapsulte some string objects with prefix and/or suffix
def Encapsulate(s):
    if len(args.prefix): s = '-'.join([args.prefix, s])
    if len(args.suffix): s = '-'.join([s, args.suffix])
    return s

# builds a basic permission statement for each qs asset type
# these are all QuickSight default permissions for an admin role
# please edit this or edit the bundle to alter futher
def BuildPermissionStatement(type, mode='rw', principal=args.principal):

    # quicksite asset permissions for sanitization
    def_permissions = {
        'ro': {
            'dashboards': [
                'quicksight:DescribeDashboard',
                'quicksight:ListDashboardVersions',
                'quicksight:QueryDashboard'
            ],
            'analyses': [
                'quicksight:DescribeAnalysisPermissions',
                'quicksight:QueryAnalysis',
                'quicksight:DescribeAnalysis'
            ],
            'datasets': [
                'quicksight:DescribeDataSet',
                'quicksight:DescribeDataSetPermissions',
                'quicksight:PassDataSet',
                'quicksight:DescribeIngestion',
                'quicksight:ListIngestions'
            ],
            'datasources': [
                'quicksight:DescribeDataSource',
                'quicksight:DescribeDataSourcePermissions',
                'quicksight:PassDataSource'
            ]
        },
        'rw': {
            'dashboards': [
                'quicksight:DescribeDashboard',
                'quicksight:ListDashboardVersions',
                'quicksight:UpdateDashboardPermissions',
                'quicksight:QueryDashboard',
                'quicksight:UpdateDashboard',
                'quicksight:DeleteDashboard',
                'quicksight:DescribeDashboardPermissions',
                'quicksight:UpdateDashboardPublishedVersion'
            ],
            'analyses': [
                'quicksight:RestoreAnalysis',
                'quicksight:UpdateAnalysisPermissions',
                'quicksight:DeleteAnalysis',
                'quicksight:DescribeAnalysisPermissions',
                'quicksight:QueryAnalysis',
                'quicksight:DescribeAnalysis',
                'quicksight:UpdateAnalysis'
            ],
            'datasets': [
                'quicksight:UpdateDataSetPermissions',
                'quicksight:DescribeDataSet',
                'quicksight:DescribeDataSetPermissions',
                'quicksight:PassDataSet',
                'quicksight:DescribeIngestion',
                'quicksight:ListIngestions',
                'quicksight:UpdateDataSet',
                'quicksight:DeleteDataSet',
                'quicksight:CreateIngestion',
                'quicksight:CancelIngestion'
            ],
            'datasources': [
                'quicksight:UpdateDataSourcePermissions',
                'quicksight:DescribeDataSource',
                'quicksight:DescribeDataSourcePermissions',
                'quicksight:PassDataSource',
                'quicksight:UpdateDataSource',
                'quicksight:DeleteDataSource'
            ]
        }
    }

    if not mode: mode = 'rw'
    return {
        'Principal': f"{principal}",
        'Actions': def_permissions[mode][type]
    }

# build permissions for asset
def BuildPermissions(type):
    perms = []
    if args.principal: perms.append(BuildPermissionStatement(type))
    if 'groups' in assets:
        for i in assets['groups']:
            perm = BuildPermissionStatement(type, mode='ro', principal=assets['groups'][i]['Arn'])
            if perm: perms.append(perm)
    return perms


###
## list APIs to retrieve asset catalogs
###

# get a catalog of themes
def list_themes():
    debug("listing themes")
    opts = { 'MaxResults': 10 }
    while True:
        o = qs.list_themes(AwsAccountId=args.account, **opts)
        for i in o['ThemeSummaryList']:
            if 'themes' not in assets: assets['themes'] = {}
            assets['themes'][i['Arn']] = i
        if 'NextToken' not in o: break
        opts['NextToken'] = o['NextToken']


# get a catalog of namespaces
def list_namespaces():
    debug("listing namespaces")
    opts = { 'MaxResults': 10 }
    while True:
        o = qs.list_namespaces(AwsAccountId=args.account, **opts)
        for i in o['Namespaces']:
            assets['namespaces'][i['Arn']] = i
        if 'NextToken' not in o: break
        opts['NextToken'] = o['NextToken']

# get a catalog of templates
def list_templates():
    debug("listing templates")
    opts = { 'MaxResults': 10 }
    while True:
        o = qs.list_templates(AwsAccountId=args.account, **opts)
        for i in o['TemplateSummaryList']:

            debug(f"retrieving versions for template {i['TemplateId']}")
            sopts = { 'MaxResults': 10, 'TemplateId': i['TemplateId'] }
            while True:
                so = qs.list_template_versions(AwsAccountId=args.account, **sopts)
                for si in so['TemplateVersionSummaryList']:
                    debug(f"retrieved a version for a template {si['Arn']}")
                    if 'Versions' not in i: i['Versions'] = {}
                    i['Versions'][si['Arn']] = si
                if 'NextToken' not in so: break
                sopts['NextToken'] = so['NextToken']

            assets['templates'][i['Arn']] = i

        if 'NextToken' not in o: break
        opts['NextToken'] = o['NextToken']

# get a catalog of dashboards
def list_dashboards():
    debug("listing dashboards")
    opts = { 'MaxResults': 10 }
    while True:
        o = qs.list_dashboards(AwsAccountId=args.account, **opts)
        for i in o['DashboardSummaryList']:

            debug(f"retrieving versions for dashboard {i['DashboardId']}")
            sopts = { 'MaxResults': 10, 'DashboardId': i['DashboardId'] }
            while True:
                so = qs.list_dashboard_versions(AwsAccountId=args.account, **sopts)
                for si in so['DashboardVersionSummaryList']:
                    debug(f"retrieved a version for a dashboard {si['Arn']}")
                    if 'Versions' not in i: i['Versions'] = {}
                    i['Versions'][si['Arn']] = si
                if 'NextToken' not in so: break
                sopts['NextToken'] = so['NextToken']

            assets['dashboards'][i['Arn']] = i
            dashboards.append(i['DashboardId'])
        if 'NextToken' not in o: break
        opts['NextToken'] = o['NextToken']

# get a catalog of analyses
def list_analyses():
    debug("listing analyses")
    opts = { 'MaxResults': 10 }
    while True:
        o = qs.list_analyses(AwsAccountId=args.account, **opts)
        for i in o['AnalysisSummaryList']:
            assets['analyses'][i['Arn']] = i
        if 'NextToken' not in o: break
        opts['NextToken'] = o['NextToken']

# get a catalog of datasets
def list_datasets():
    debug("listing datasets")
    opts = { 'MaxResults': 10 }
    while True:
        o = qs.list_data_sets(AwsAccountId=args.account, **opts)
        for i in o['DataSetSummaries']:

            debug(f"retrieving ingestions for dataset {i['DataSetId']}")
            sopts = { 'MaxResults': 10, 'DataSetId': i['DataSetId'] }
            while True:
                so = qs.list_ingestions(AwsAccountId=args.account, **sopts)
                for si in so['Ingestions']:
                    debug(f"retrieved a ingestions for a dataset {si['Arn']}")
                    if 'Ingestions' not in i: i['Ingestions'] = {}
                    i['Ingestions'][si['Arn']] = si
                if 'NextToken' not in so: break
                sopts['NextToken'] = so['NextToken']

            debug(f"retrieving refresh schedules for dataset {i['DataSetId']}")
            sopts = { 'MaxResults': 10, 'DataSetId': i['DataSetId'] }
            so = qs.list_refresh_schedules(AwsAccountId=args.account, DataSetId=i['DataSetId'])
            if 'RefreshSchedules' in so: i['RefreshSchedules'] = so['RefreshSchedules']

            assets['datasets'][i['Arn']] = i
        if 'NextToken' not in o: break
        opts['NextToken'] = o['NextToken']

# get a catalog of datasources
def list_datasources():
    debug("retrieving datasource catalog")

    opts = { 'MaxResults': 10 }
    while True:
        o = qs.list_data_sources(AwsAccountId=args.account, **opts)
        for i in o['DataSources']:
            assets['datasources'][i['Arn']] = i
        if 'NextToken' not in o: break
        opts['NextToken'] = o['NextToken']


# get a catalog of groups
# bug - should cycle through above and already retreived namespace catalog
def list_groups():
    debug("retrieving group catalog")

    opts = { 'MaxResults': 10, 'Namespace':'default' }
    while True:
        o = qs.list_groups(AwsAccountId=args.account, **opts)
        for i in o['GroupList']:
            assets['groups'][i['Arn']] = i
        if 'NextToken' not in o: break
        opts['NextToken'] = o['NextToken']


###
## describe APIs to retrieve asset descriptions
###

# describe a dashboard
def describe_dashboard(i):
    try:
        debug(f"retrieving dashboard definition {i}")
        asset = qs.describe_dashboard_definition(AwsAccountId=args.account, DashboardId=i)
        perms = qs.describe_dashboard_permissions(AwsAccountId=args.account, DashboardId=i)
        asset['Permissions'] = perms['Permissions']
        asset['Name'] = Encapsulate(asset['Name'])
        asset['DashboardId'] = Encapsulate(asset['DashboardId'])

        for perm in perms['Permissions']:
            rm = re.match(r'(?i)(arn:aws:quicksight:[^:]*:[^:]*:(group)/default/(.+))', perm['Principal'])
            if rm and rm.group(2) in ['group']:
                group = describe_group(rm.group(3))

        assets["dashboards"][asset["DashboardId"]] = asset

    except Exception as e:
        err = 0 if args.ignore else 255
        debug(f"!! dashboard {e}", err)

    return asset

# describe an analysis
def describe_analysis(i):
    try:
        debug(f"retrieving analysis definition {i}")
        asset = qs.describe_analysis_definition(AwsAccountId=args.account, AnalysisId=i)
        perms = qs.describe_analysis_permissions(AwsAccountId=args.account, AnalysisId=i)
        asset['Permissions'] = perms['Permissions']
        asset['Name'] = Encapsulate(asset['Name'])
        asset['AnalysisId'] = Encapsulate(asset['AnalysisId'])

        for perm in perms['Permissions']:
            rm = re.match(r'(?i)(arn:aws:quicksight:[^:]*:[^:]*:group/default/(.+))', perm['Principal'])
            if rm and rm.group(2) in ['TestGroup']:
                group = describe_group(rm.group(2))

        assets["analyses"][asset["AnalysisId"]] = asset
    except Exception as e:
        err = 0 if args.ignore else 255
        debug(f"!! analysis {e}", err)
    return asset

# describe a dataset
def describe_dataset(i):
    debug(f"retrieving datasets, permissions, and refresh schedule(s) {i}")
    try:
        asset = qs.describe_data_set(AwsAccountId=args.account, DataSetId=i)['DataSet']
        perms = qs.describe_data_set_permissions(AwsAccountId=args.account, DataSetId=i)
        if 'Permissions' in asset: asset['Permissions'] = perms['Permissions']

        for perm in perms['Permissions']:
            rm = re.match(r'(?i)(arn:aws:quicksight:[^:]*:[^:]*:group/default/(.+))', perm['Principal'])
            if rm and rm.group(2) in ['TestGroup']:
                group = describe_group(rm.group(2))

        ar = []
        schedules = qs.list_refresh_schedules(AwsAccountId=args.account, DataSetId=i)
        for schedule in schedules['RefreshSchedules']:
            if 'ScheduleId' not in schedule: next
            rs = qs.describe_refresh_schedule(AwsAccountId=args.account, DataSetId=i, ScheduleId=schedule['ScheduleId'])
            if 'RefreshSchedule' in rs: ar.append(rs['RefreshSchedule'])
        if len(ar): asset['RefreshSchedules'] = ar

        asset['Name'] = Encapsulate(asset['Name'])
        asset['DataSetId'] = Encapsulate(asset['DataSetId'])

        assets["datasets"][i] = asset
    except Exception as e:
        err = 0 if args.ignore else 255
        debug(f"!! dataset {e}", err)

    return asset

# describe a datasource
def describe_datasource(i):
    debug(f"retrieving datasource and permissions {i}")
    try:
        asset = qs.describe_data_source(AwsAccountId=args.account, DataSourceId=i)['DataSource']
        perms = qs.describe_data_source_permissions(AwsAccountId=args.account, DataSourceId=i)
        asset['Permissions'] = perms['Permissions']
        asset['Name'] = Encapsulate(asset['Name'])
        asset['DataSourceId'] = Encapsulate(asset['DataSourceId'])

        for perm in perms['Permissions']:
            rm = re.match(r'(?i)(arn:aws:quicksight:[^:]*:[^:]*:group/default/(.+))', perm['Principal'])
            if rm and rm.group(2) in ['TestGroup']:
                group = describe_group(rm.group(2))

        assets["datasources"][i] = asset
    except Exception as e:
        err = 0 if args.ignore else 255
        debug(f"!! datasource {e}", err)
    return asset


# describe a datasource
def describe_group(i):
    debug(f"retrieving group {i}")
    try:
        asset = qs.describe_group(AwsAccountId=args.account, GroupName=i, Namespace='default')['Group']
        asset['GroupName'] = Encapsulate(asset['GroupName'])
        asset['PrincipalId'] = Encapsulate(asset['PrincipalId'])

        assets["groups"][i] = asset
    except Exception as e:
        err = 0 if args.ignore else 255
        debug(f"!! group {e}", err)
    return asset


###
## create/update/delete APIs to provosion assets
###

# create/deploy a dashboard
def deploy_dashboard(obj):
    if not args.nofollow:
        for d in obj['Definition']['DataSetIdentifierDeclarations']:
            ds = d['DataSetArn'].split('/')[-1]
            result = deploy_dataset(assets['datasets'][ds])
            d['DataSetArn'] = result['Arn']

    debug(f"{args.action} dashboard {obj['DashboardId']}")
    for i in ['ResponseMetadata','Status','ResourceStatus','RequestId']:
        if i in obj: del obj[i]
    obj['Name'] = Encapsulate(obj['Name'])
    obj['DashboardId'] = Encapsulate(obj['DashboardId'])
    result = None
    try:
        if args.action in ['delete']:
            result = qs.delete_dashboard(AwsAccountId=args.account, DashboardId=obj['DashboardId'])
        elif args.action in ['create']:
            result = qs.create_dashboard( AwsAccountId=args.account, **obj)
        elif args.action in ['update']:
            for i in ['Permissions']:
                if i in obj: del obj[i]
            result = qs.update_dashboard( AwsAccountId=args.account, **obj)
        results.append(json.dumps(result, cls=DateTimeEncoder, indent=4))
    except Exception as e:
        err = 0 if args.ignore else 255
        debug(f"!! dashboard {e}", err)
    return result

# create/deploy an analysis
def deploy_analysis(obj):
    if not args.nofollow:
        for d in obj['Definition']['DataSetIdentifierDeclarations']:
            ds = d['DataSetArn'].split('/')[-1]
            result = deploy_dataset(assets['datasets'][ds])
            d['DataSetArn'] = result['Arn']

    debug(f"{args.action} analysis {obj['AnalysisId']}")
    for i in ['ResponseMetadata','Status','ResourceStatus','RequestId']:
        if i in obj: del obj[i]
    obj['Name'] = Encapsulate(obj['Name'])
    obj['AnalysisId'] = Encapsulate(obj['AnalysisId'])
    result = None
    try:
        if args.action in ['delete']:
            result = qs.delete_analysis(AwsAccountId=args.account, AnalysisId=obj['AnalysisId'])
        elif args.action in ['create']:
            result = qs.create_analysis( AwsAccountId=args.account, **obj)
        elif args.action in ['update']:
            for i in ['Permissions']:
                if i in obj: del obj[i]
            result = qs.update_analysis( AwsAccountId=args.account, **obj)
        results.append(json.dumps(result, cls=DateTimeEncoder, indent=4))
    except Exception as e:
        err = 0 if args.ignore else 255
        debug(f"!! analysis {e}", err)
    return result

# create/deploy a dataset
def deploy_dataset(obj):
    if not args.nofollow:
        for d in obj['PhysicalTableMap']:
            ds = obj['PhysicalTableMap'][d]['CustomSql']['DataSourceArn'].split('/')[-1]
            result = deploy_datasource(assets['datasources'][ds])
            obj['PhysicalTableMap'][d]['CustomSql']['DataSourceArn'] = result['Arn']

    debug(f"{args.action} dataset {obj['DataSetId']}")
    for i in ['CreatedTime','LastUpdatedTime','Status','Arn','ConsumedSpiceCapacityInBytes','OutputColumns']:
        if i in obj: del obj[i]
    obj['Name'] = Encapsulate(obj['Name'])
    obj['DataSetId'] = Encapsulate(obj['DataSetId'])
    result = None
    schedules = []

    try:
        if args.action in ['delete']:
            result = qs.delete_data_set(AwsAccountId=args.account, DataSetId=obj['DataSetId'])
        elif args.action in ['create']:
            if 'RefreshSchedules' in obj:
                schedules = obj['RefreshSchedules']
                del obj['RefreshSchedules']
            result = qs.create_data_set( AwsAccountId=args.account, **obj)
            for s in schedules:
                futuretime = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=5)
                s['StartAfterDateTime'] = futuretime.astimezone(datetime.timezone.utc).replace(microsecond=0).isoformat()
                result = qs.create_refresh_schedule(AwsAccountId=args.account, DataSetId=obj['DataSetId'], Schedule=s)
        elif args.action in ['update']:
            for i in ['Permissions']:
                if i in obj: del obj[i]
            if 'RefreshSchedules' in obj:
                schedules = obj['RefreshSchedules']
                del obj['RefreshSchedules']
            result = qs.update_data_set( AwsAccountId=args.account, **obj)
            for s in schedules:
                futuretime = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=5)
                s['StartAfterDateTime'] = futuretime.astimezone(datetime.timezone.utc).replace(microsecond=0).isoformat()
                result = qs.update_refresh_schedule(AwsAccountId=args.account, DataSetId=obj['DataSetId'], Schedule=s)
        results.append(json.dumps(result, cls=DateTimeEncoder, indent=4))

    except Exception as e:
        err = 0 if args.ignore else 255
        debug(f"!! dataset {e}", err)
    return result

# create/deploy a datasource
def deploy_datasource(obj):
    debug(f"{args.action} datasource {obj['DataSourceId']}")
    for i in ['CreatedTime','LastUpdatedTime','Status', 'Arn']:
        if i in obj: del obj[i]
    obj['Name'] = Encapsulate(obj['Name'])
    obj['DataSourceId'] = Encapsulate(obj['DataSourceId'])
    result = None
    try:
        if args.action in ['delete']:
            result = qs.delete_data_source(AwsAccountId=args.account, DataSourceId=obj['DataSourceId'])
        elif args.action in ['create']:
            result = qs.create_data_source( AwsAccountId=args.account, **obj)
        elif args.action in ['update']:
            for i in ['Permissions', 'Type']:
                if i in obj: del obj[i]
            result = qs.update_data_source( AwsAccountId=args.account, **obj)
        results.append(json.dumps(result, cls=DateTimeEncoder, indent=4))
    except Exception as e:
        err = 0 if args.ignore else 255
        debug(f"!! datasource {e}", err)
    return result


# create/deploy a group
def deploy_group(obj):
    debug(f"{args.action} group {obj['GroupName']}")
    for i in ['CreatedTime','LastUpdatedTime','Status', 'Arn']:
        if i in obj: del obj[i]
    obj['GroupName'] = Encapsulate(obj['GroupName'])
    obj['PrincipalId'] = Encapsulate(obj['PrincipalId'])
    obj['Namespace'] = 'default'
    result = None
    try:
        if args.action in ['delete']:
            result = qs.delete_group(AwsAccountId=args.account, GroupName=obj['GroupName'], Namespace='default')
        elif args.action in ['create']:
            result = qs.create_group(AwsAccountId=args.account, GroupName=obj['GroupName'], Namespace='default')
        elif args.action in ['update']:
            for i in ['Permissions']:
                if i in obj: del obj[i]
            result = qs.delete_group(AwsAccountId=args.account, GroupName=obj['GroupName'], Namespace='default')
        results.append(json.dumps(result, cls=DateTimeEncoder, indent=4))
    except Exception as e:
        err = 0 if args.ignore else 255
        debug(f"!! group {e}", err)
    return result


###
## Perform requested action directives
###

###
## Enumerate assets and write catalog to a file
###

if args.action in ['list']:
    if not len(args.type):
        args.type = "all"

    # used for lookups for retrieving dashboard versions            
    dashboards = []

    # retrieve a catalog of namespaces
    if args.type in ['theme', 'all']:
        list_themes()

    # retrieve a catalog of namespaces
    if args.type in ['namespace', 'all']:
        list_namespaces()

    # retrieve a catalog of templates
    if args.type in ['template', 'all']:
        list_templates()

    # retrieve a catalog of dashboards
    if args.type in ['dashboard', 'all']:
        list_dashboards()

    # retrieve a catalog of analyses
    if args.type in ['analysis', 'all']:
        list_analyses()
            
    # retrieve a catalog of datasets
    if args.type in ['dataset', 'all']:
        list_datasets()

    # retrieve a catalog of datasources
    if args.type in ['datasource', 'all']:
        list_datasources()

    # retrieve a catalog of groups
    if args.type in ['group', 'all']:
        list_groups()

    debug(f"exporting catalog of assets {args.catalog}")
    with open(args.catalog, 'w') as file:
        file.write(json.dumps(assets, cls=DateTimeEncoder, indent=4))

###
## Describe assets and save an asset bundle
###

elif args.action in ['describe']:
    if not len(args.ids):
        debug('!! you must provide asset IDs to bundle', 255)

    if args.preopen:
        debug(f"preopening deployable assets from {args.assets}")
        with open(args.assets, 'r') as file:
            assetsFile = file.read()
        assets = json.loads(assetsFile)

    # the latch is used to retrieve all dependent objects
    # the latch is engaged with --follow
    latch = False

    # used for dependency tracking and lookups when using the latch
    datasetids = []
    datasourceids = []
    groupids = []

    # exports dashboards
    if args.type in ['dashboard']:
        for i in args.ids:
            asset = describe_dashboard(i)
            if not args.nofollow:
                latch = True
                for x in asset['Definition']['DataSetIdentifierDeclarations']:
                    datasetids.append(x['DataSetArn'].split('/')[-1])

    # exports analyses
    if args.type in ['analysis']:
        # retrieve the analysis
        for i in args.ids:
            asset = describe_analysis(i)
            if not args.nofollow:
                latch = True
                for x in asset['Definition']['DataSetIdentifierDeclarations']:
                    datasetids.append(x['DataSetArn'].split('/')[-1])

    # exports datasets
    if args.type in ['dataset'] or latch:
        ids = datasetids if latch else args.ids
        for i in ids:
            asset = describe_dataset(i)
            if not args.nofollow:
                latch = True
                for x in asset['PhysicalTableMap']:
                    o = asset['PhysicalTableMap'][x]
                    datasourceids.append(o['CustomSql']['DataSourceArn'].split('/')[-1])

    # exports datasources
    if args.type in ['datasource'] or latch:
        ids = datasourceids if latch else args.ids
        for i in ids:
            asset = describe_datasource(i)

    # exports groups
    if args.type in ['group'] or latch:
        ids = groupids if latch else args.ids
        for i in ids:
            asset = describe_group(i)

    # write collected exports to file
    debug(f"exporting bundle of assets {args.assets}")
    with open(args.assets, 'w') as file:
        file.write(json.dumps(assets, cls=DateTimeEncoder, indent=4))

###
## Sanitize the asset bundle for distribution or deployment to another account.
###

elif args.action in ['sanitize']:
    debug(f"sanitizing asset bundle and updating permissions from asset bundle {args.assets}")

    debug(f"performing full string regex replacements {args.assets}")
    def Sanitize(dirty):

        # sanitize arn regex - updates to current account
        # (either --account or sts:get-caller-identity)
        dirty = re.sub(r'(?i)("(arn:aws:quicksight):([^:]*):([^aws:]*):([^"]+))"', '"\\2:<aws-region>:<aws-account>:\\5"', dirty)
        if args.region: dirty = re.sub( r'(?i)<aws-region>', f'{args.region}', dirty)
        if args.account: dirty = re.sub( r'(?i)<aws-account>', f'{args.account}', dirty)

        # correct region for Amazon Security Lake
        # amazon_security_lake_glue_db_us_east_1
        # amazon_security_lake_table_us_east_1_vpc_flow
        if args.asl and not args.slregion: args.slregion = args.asl
        if not args.slregion: args.slregion = args.region # default to single region if not --slregion
        if args.slregion: args.slregion = re.sub(r'-', '_', args.slregion) # sanity check
        dirty = re.sub( r'(?i)(amazon_security_lake_glue_db_)([^_]+_[^_]+_\d+)', f'\\1<aws-security-lake-region>', dirty)       # database name
        dirty = re.sub( r'(?i)(amazon_security_lake_table_)([^_]+_[^_]+_\d+)(_.+)', f'\\1<aws-security-lake-region>\\3', dirty)    # table name
        if args.slregion:
            dirty = re.sub( r'(?i)<aws-security-lake-region>', f'{args.slregion}', dirty, count=0)

        return dirty # more clean

    # opens, reads string, full-text-regexes, writes, and closes
    with open(args.assets, 'r') as file:
        dirty = file.read()
    sanitized = Sanitize(dirty)
    with open(args.assets, 'w') as file:
        file.write(sanitized)

    # now open and go through each object
    debug(f"removing specific objects")
    with open(args.assets, 'r') as file:
        assetsFile = file.read()
    assets = json.loads(assetsFile)

    # remove unnecessary data points and correct permissions
    debug(f"removing unnecessary dashboard objects")
    for i in assets['dashboards']:
        for o in ['ResponseMetadata', 'ResourceStatus', 'RequestId', 'Status', 'Permissions']:
            if o in assets['dashboards'][i]: del assets['dashboards'][i][o]
        perms = BuildPermissions('dashboards')
        if perms: assets['dashboards'][i]['Permissions'] = perms

    # remove unnecessary data points
    debug(f"removing unnecessary analysis objects")
    for i in assets['analyses']:
        for o in ['ResponseMetadata', 'ResourceStatus', 'RequestId', 'Status', 'Permissions']:
            if o in assets['analyses'][i]: del assets['analyses'][i][o]
        perms = BuildPermissions('analyses')
        if perms: assets['analyses'][i]['Permissions'] = perms

    # remove unnecessary data points
    debug(f"removing unnecessary dataset objects")
    for i in assets['datasets']:
        for o in ['CreatedTime', 'LastModifiedTime', 'Status', 'Permissions']:
            if o in assets['datasets'][i]: del assets['datasets'][i][o]
        perms = BuildPermissions('datasets')
        if perms: assets['datasets'][i]['Permissions'] = perms

    # remove unnecessary data points
    debug(f"removing unnecessary datasource objects")
    for i in assets['datasources']:
        for o in ['CreatedTime', 'LastModifiedTime', 'Status', 'Permissions']:
            if o in assets['datasources'][i]: del assets['datasources'][i][o]
        perms = BuildPermissions('datasources')
        if perms: assets['datasources'][i]['Permissions'] = perms

    debug("sanitized")

    # write collected exports to file
    debug(f"exporting bundle of assets {args.assets}")
    with open(args.assets, 'w') as file:
        file.write(json.dumps(assets, cls=DateTimeEncoder, indent=4))


###
## Deploy the asset bundle - create, update, or delete
###

elif args.action in ['create', 'update', 'delete']:

    if args.action in ['delete'] and not args.confirm:
        debug('!! verify that you are DEPLOYING into the DESTINATION account')
        debug('!! asset deletion requires confirmation with --confirm', 255)

    debug(f"reading deployable assets from {args.assets}")
    with open(args.assets, 'r') as file:
        assetsFile = file.read()
    assets = json.loads(assetsFile)

    # deploys assets along with their dependencies
    if args.type in ['dashboard']:
        for i in args.ids:
            result = deploy_dataset(assets['dashboards'][i])
    elif args.type in ['analysis']:
        for i in args.ids:
            result = deploy_analysis(assets['analyses'][i])
    elif args.type in ['dataset']:
        for i in args.ids:
            result = deploy_dataset(assets['datasets'][i])
    elif args.type in ['datasource']:
        for i in args.ids:
            result = deploy_datasource(assets['datasources'][i])
    elif args.type in ['group']:
        for i in args.ids:
            result = deploy_group(assets['groups'][i])

    # deploy everything in the assets file
    elif args.type in ['all']:
        if not args.nofollow: args.nofollow = True
        if 'groups' in assets:
            for i in assets['groups']:
                result = deploy_group(assets['groups'][i])
        if 'datasources' in assets:
            for i in assets['datasources']:
                result = deploy_datasource(assets['datasources'][i])
        if 'datasets' in assets:
            for i in assets['datasets']:
                result = deploy_dataset(assets['datasets'][i])
        if 'analyses' in assets:
            for i in assets['analyses']:
                result = deploy_analysis(assets['analyses'][i])
        if 'dashboards' in assets:
            for i in assets['dashboards']:
                result = deploy_dashboard(assets['dashboards'][i])

    # append collected results to file
    debug(f"appending output to {args.output}")
    with open(args.output, 'a') as file:
        file.write(json.dumps(results, cls=DateTimeEncoder, indent=4))


# cleanup
qs.close()
exit(0)

# eof
