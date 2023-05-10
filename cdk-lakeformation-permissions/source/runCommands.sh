echo "--------------------------------"
echo "Running cdk deploy --all command"
echo "--------------------------------"
cdk deploy --all -v --debug
echo "--------------------------------"
echo "Finished cdk deploy"
echo "--------------------------------"
python3 ../../qs_lake_generate.py --account ACCOUNTID  --principal QUICKSIGHTUSERARN --region us-east-1 --slregion us-east-1 