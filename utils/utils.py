import sys
import logging
from azure.storage.blob import BlobClient
from django.core.files.uploadedfile import SimpleUploadedFile

def uploadDateToAzureBlobStorage(data, formid):
    CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=assoconnect1234;AccountKey=1zn10lzx9VYbeYwTPFDeSvRkiPeG3zMMYcsvXDiOJEqq6sPyQibug9mDHUt0dC8ioInZIWm7nO7L0BTzR0fgdQ==;EndpointSuffix=core.windows.net"
    CONTAINER_NAME  = "assoconnect-images"
    BLOB_NAME = "{}-{}".format(str(data), formid)
    
    # Create a logger for the 'azure.storage.blob' SDK
    blob = BlobClient.from_connection_string(conn_str=CONNECTION_STRING, container_name=CONTAINER_NAME, blob_name=BLOB_NAME)

    blob.upload_blob(data)
  




