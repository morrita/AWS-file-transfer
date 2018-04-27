import boto3

s3_client = boto3.client('s3')
destination_bucket_name = 'outbound-filestore'

def lambda_handler(event, context):
    
    source_bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = event['Records'][0]['s3']['object']['key']
    copy_source = source_bucket_name + '/' + file_name
    
#   uncomment below for de-bugging     
#    print("Source bucket name = %s\n" % (source_bucket_name))
#    print("File name received = %s\n" % (file_name))
#    print("Destination bucket = %s\n" % (destination_bucket_name))
#    print("CopySource = %s\n" % (copy_source))
    
    s3_client.copy_object(CopySource=copy_source, Bucket=destination_bucket_name, Key=file_name)
    
    return 