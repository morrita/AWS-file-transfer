# lambda_function.py

import boto3
import os 
import sys

from function_library import get_date
from function_library import copy_file
from function_library import delete_file
from function_library import move_file
from function_library import get_outbound_bucket
  
def lambda_handler(event, context):
    
    
    # check for verbose flag environment variable and set appropriately
    if 'verbose' in os.environ:
         if os.environ['verbose'].lower() == 'true':    
            verbose = True
         else:
            verbose = False
    else: 
        verbose = False  # False by default
    
    
    s3_client = boto3.client('s3')
    error_bucket_name = 'error-filestore'
    source_bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = event['Records'][0]['s3']['object']['key']
    file_list = file_name.split('_')
    application_name =   file_list[0]
  
    
    if application_name != file_name:  # application name found okay
        if verbose:
            datestr = get_date()
            print ("INFO: application name read from filename string = %s at %s\n" % (application_name, datestr)) 
            
        destination_bucket_name = get_outbound_bucket(application_name=application_name, verbose=verbose, error_bucket=error_bucket_name)
        
    else:
        destination_bucket_name = error_bucket_name # direct file with no application name to error bucket and log error
        datestr = get_date()
        print ("ERROR: application name not provide - moving to bucket %s at %s\n" % (error_bucket_name, datestr))   


    if move_file(source_bucket=source_bucket_name, destination_bucket=destination_bucket_name, file_name=file_name, verbose=verbose, s3_client=s3_client, error_bucket=error_bucket_name):
        datestr = get_date()
        print ("INFO: filename %s in bucket %s successfully moved to bucket %s at %s\n" % (file_name, source_bucket_name,destination_bucket_name, datestr))    
        
    else:
        datestr = get_date()
        print ("ERROR: there was a problem processing filename %s in bucket %s at %s\n" % (file_name, source_bucket_name, datestr))   
        
    return 
