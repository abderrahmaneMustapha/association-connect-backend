from azure.storage.blob import BlobClient
from azure.storage.blob import ContainerClient

from django.core.files.uploadedfile import SimpleUploadedFile


CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=assoconnect1234;AccountKey=1zn10lzx9VYbeYwTPFDeSvRkiPeG3zMMYcsvXDiOJEqq6sPyQibug9mDHUt0dC8ioInZIWm7nO7L0BTzR0fgdQ==;EndpointSuffix=core.windows.net"
CONTAINER_NAME  = "assoconnect-images"

def uploadDataToAzureBlobStorage(data, title, associationid):

      
    BLOB_NAME = "{}-{}.jpg".format(associationid,title)
    
    # Create a logger for the 'azure.storage.blob' SDK
    blob = BlobClient.from_connection_string(conn_str=CONNECTION_STRING, container_name=CONTAINER_NAME, blob_name=BLOB_NAME)

    blob.upload_blob(data)

    return blob.url

def deleteDataFromAzureBlobStorage(data, title, associationid):
    BLOB_NAME = "{}-{}.jpg".format(associationid,title)
    
    # Create a logger for the 'azure.storage.blob' SDK
    blob = ContainerClient.from_connection_string(conn_str=CONNECTION_STRING, container_name=CONTAINER_NAME)

    blob.delete_blob(blob=BLOB_NAME)


def excludNullFields(inputs):
   
    del inputs['email']
    return {
        k:v
        for k, v in inputs.items()
        if v 
    }
  




