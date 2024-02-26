import boto3
from datetime import datetime, timedelta

PARAMS=[
    '/sop/OPEN_AI/key' 
]
REGION='us-east-1'

def get_credentials(params=None):
    if params is None:
        params = PARAMS
    ssm = boto3.client('ssm',REGION)
    response = ssm.get_parameters(
      Names=params,
      WithDecryption=True
    )
    # Build dict of keys
    param_values={k['Name']:k['Value'] for k in  response['Parameters']}
    return param_values
