#  "serializeImageData"

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event['s3_key'] ## TODO: fill in
    bucket =event['s3_bucket']  ## TODO: fill in

    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    s3.download_file(bucket, key, "/tmp/image.png")

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }



# responsible for the classification part -
#    we're going to take the image output from the previous function, 
# decode it, and then pass inferences back to the the Step Function.

# classificationtask


import json
import base64
import boto3

# Using low-level client representing Amazon SageMaker Runtime ( To invoke endpoint)
runtime_client = boto3.client('sagemaker-runtime')                   


# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2023-10-27-21-29-04-339" ## TODO: fill in (Trained IC Model Name)


def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['image_data'])     ## TODO: fill in (Decoding the encoded 'Base64' image-data and class remains'bytes')

   
    response = runtime_client.invoke_endpoint(
                                        EndpointName=ENDPOINT,    
                                        Body=image,              
                                        ContentType='image/png'  
                                    )
                                    
    
   
    
    ## TODO: fill in (Read and decode predictions/inferences to 'utf-8' & convert JSON string obj -> Python object)
    inferences = json.loads(response['Body'].read().decode('utf-8'))     # list
  
    
    # We return the data back to the Step Function    
    event['inferences'] = inferences            ## List of predictions               
    return {
        'statusCode': 200,
        'body': event                           ## Passing the event python dictionary in the body
    }




# Finally, we need to filter low-confidence inferences. 
# Define a threshold between 1.00 and 0.000 for your model: 
# what is reasonble for you? If the model predicts at .70 for 
# it's highest confidence label, do we want to pass that inference
# along to downstream systems? Make one last Lambda function and tee up the same permissions:

# filter_inferences

import json

THRESHOLD = .75

def lambda_handler(event, context):

    # Grab the inferences from the event
    inferences =event['inferences'] ## TODO: fill in

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold =max(list(inferences))>THRESHOLD  ## TODO: fill in

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
