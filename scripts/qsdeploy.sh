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
python3 qs_lake_generate.py
echo "Finished QuickSight Generate Dashboards"
echo "--------------------------------------------"
