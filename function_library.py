# function_library.py


def check_public_access_allowed(application_name, dynamodb_table, aws_region, verbose): 
    import boto3
    from boto3.dynamodb.conditions import Key
    
    public_access_allowed = False
    
    dynamodb = boto3.resource('dynamodb', region_name=aws_region)
    table = dynamodb.Table(dynamodb_table)
    response = table.query(KeyConditionExpression=Key('APPLICATION_NAME').eq(application_name))
    
    if response['Items']:       # valid response from database
        if response['Items'][0]['PUBLIC_ACCESS_ALLOWED'].lower() == "true":
             public_access_allowed = True
             
        else:
            if verbose:
                datestr = get_date()
                print ("INFO: response = %s read from DynamoDB table %s for application %s at %s\n" % (response['Items'][0]['PUBLIC_ACCESS_ALLOWED'],application_name,dynamodb_table, datestr))  
        
    else:
        if verbose:
            datestr = get_date()
            print ("ERROR: non-valid response read from DynamoDB table %s for application %s at %s\n" % (dynamodb_table, application_name, datestr))  
    
    if verbose:
        datestr = get_date()
        print ("INFO: public_access_allowed set to %s at %s\n" % (public_access_allowed, datestr))  
    
    return public_access_allowed


def check_public_s3_access(s3_client, bucket_name, verbose):
    public_access = False
    acl = s3_client.get_bucket_acl(Bucket=bucket_name)
  
    for i in range (len(acl['Grants'])):
        if acl['Grants'][i]['Grantee']['Type'] == 'Group':
            if acl['Grants'][i]['Grantee']['URI'] == 'http://acs.amazonaws.com/groups/global/AllUsers':
                public_access = True
                
                if verbose:
                    datestr = get_date()
                    print ("INFO: public %s permission on bucket %s detected at %s\n" % (acl['Grants'][i]['Permission'],bucket_name, datestr))       
    return public_access

def get_outbound_bucket(application_name, verbose, error_bucket,dynamodb_table, aws_region):
    import boto3
    from boto3.dynamodb.conditions import Key
    
    dynamodb = boto3.resource('dynamodb', region_name=aws_region)
    table = dynamodb.Table(dynamodb_table)
    response = table.query(KeyConditionExpression=Key('APPLICATION_NAME').eq(application_name))
    
    if response['Items']:       # valid response from database
        bucket_name = response['Items'][0]['TARGET_BUCKET']
        
    else:
        bucket_name = error_bucket
        datestr = get_date()
        print ("ERROR: application %s not found in database - directing file to %s at %s\n" % (application_name, error_bucket, datestr))  
    
    if verbose:
        datestr = get_date()
        print ("INFO: destination bucket name being returned = %s at %s\n" % (bucket_name, datestr))  
        
    return bucket_name

def get_date(): # return current date and time
        from datetime import datetime
        time = datetime.now()
        return "%02d-%02d-%04d %02d:%02d:%02d" % (time.day, time.month, time.year, time.hour, time.minute, time.second)
        
  
def delete_file(bucket_name,file_name,verbose,s3_client):
    if verbose:
        datestr = get_date()
        print ("INFO: deleting filename %s from %s at %s\n" % (file_name, bucket_name, datestr))  
    
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        
        if verbose:
            datestr = get_date()
            print ("INFO: filename %s successfully deleted from %s at %s\n" % (file_name, bucket_name, datestr))
        return True
        
    except:
        datestr = get_date()
        print ("ERROR: an error occurred deleting filename %s from %s at %s\n" % (file_name, bucket_name, datestr)) 
        return False  
        
    
def copy_file(source_bucket,destination_bucket, file_name, verbose, s3_client):
    copy_source = source_bucket + '/' + file_name
    if verbose:
        datestr = get_date()
        print ("INFO: copying filename %s from %s to %s at %s\n" % (file_name, source_bucket, destination_bucket, datestr))
    
    try:
        s3_client.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=file_name)
        
        if verbose:
            datestr = get_date()
            print ("INFO: filename %s successfully copied from %s to %s at %s\n" % (file_name, source_bucket, destination_bucket, datestr))
        return True
        
    except:
        datestr = get_date()
        print ("ERROR: an error occurred copying filename %s from %s to %s at %s\n" % (file_name, source_bucket, destination_bucket, datestr)) 
        return False  
        
def move_file(source_bucket, destination_bucket, file_name, verbose, s3_client, error_bucket):
    
    if copy_file(source_bucket=source_bucket, destination_bucket=destination_bucket, file_name=file_name, verbose=verbose, s3_client=s3_client):
        
        if delete_file(bucket_name=source_bucket,file_name=file_name,verbose=verbose,s3_client=s3_client):
            if verbose:
                datestr = get_date()
                print ("INFO: filename %s in bucket %s successfully processed at %s\n" % (file_name, source_bucket, datestr)) 
            return True
            
        else:
            datestr = get_date()
            print ("ERROR: failed to delete filename %s in bucket %s at %s\n" % (file_name, source_bucket_name, datestr))  
            return False
            
    elif not copy_file(source_bucket=source_bucket, destination_bucket=error_bucket, file_name=file_name, verbose=verbose, s3_client=s3_client):
            if verbose:
                datestr = get_date()
                print ("INFO: leaving filename %s in bucket %s at %s\n" % (file_name, source_bucket, datestr)) 
            return False
