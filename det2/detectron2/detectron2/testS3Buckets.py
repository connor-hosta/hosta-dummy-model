import boto3

ACCESS_ID = 'AKIAX4ZVYN4EJL3JPPUJ'
ACCESS_KEY = 'm2VoUUE0SWLFtXco3yS8gpTplC2M78GZiPaqUtVo'

AWS_REGION = "us-east-2"
client = boto3.client("s3", region_name=AWS_REGION, aws_access_key_id=ACCESS_ID,
         aws_secret_access_key= ACCESS_KEY)

response = client.list_buckets()

print("Listing Amazon S3 Buckets:")

for bucket in response['Buckets']:
    print(f"-- {bucket['Name']}")