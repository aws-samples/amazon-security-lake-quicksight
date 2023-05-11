#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path/cdk-lakeformation-permissions/source"
echo "Running cdk synth and deploy --all command"
echo "--------------------------------------------"
echo " "
cdk synth
cdk deploy --all -v
echo "Finished cdk deploy"
echo "--------------------------------------------"
echo "Running QuickSight Generate Dashboards"
echo "--------------------------------------------"
echo " "
python3 ../../scripts/createqsobjects.py
echo "Finished QuickSight Generate Dashboards"
echo "--------------------------------------------"