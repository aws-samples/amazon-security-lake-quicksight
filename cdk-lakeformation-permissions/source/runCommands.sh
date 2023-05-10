echo "--------------------------------"
echo "Running cdk deploy --all command"
echo "--------------------------------"
cdk deploy --all -v
echo "--------------------------------"
echo "Finished cdk deploy"
echo "--------------------------------"
echo "--------------------------------"
echo "Running QuickSight Generate Dashboards"
echo "--------------------------------"
python3 ../../qs_lake_generate.py
echo "--------------------------------"
echo "Finished QuickSight Generate Dashboards"
echo "--------------------------------"