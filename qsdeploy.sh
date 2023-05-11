#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
echo $parent_path
cd "$parent_path/cdk-lakeformation-permissions/source"
echo $(pwd)
echo "Running cdk deploy --all command"
echo "--------------------------------------------"
echo " "
cdk deploy --all -v
echo "Finished cdk deploy"
echo "--------------------------------------------"

# echo "Running QuickSight Generate Dashboards"
# echo "--------------------------------------------"
# echo " "
# python3 createobjects.py
# echo "Finished QuickSight Generate Dashboards"
# echo "--------------------------------------------"
