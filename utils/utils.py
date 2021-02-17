from azure.storage.blob import BlobClient
from azure.storage.blob import ContainerClient

from django.core.files.uploadedfile import SimpleUploadedFile

from .forms import *
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


def excludNullFields(inputs, exclude):
   
    del inputs[exclude]
    return {
        k:v
        for k, v in inputs.items()
        if v 
    }
  
def validateData(data,field):
        field_type_name  = field.type.name
        try : 
           
            valide_choices_fields = ["checkbox", "radio", "select"]
            if (field_type_name == "short-text"):
                form = ValidateShortTextFieldForm(data=data)
                throwInvalideDataException(form)

            if (field_type_name == "long-text"):
                form = ValidateLongTextFieldForm(data=data)
                throwInvalideDataException(form)

            if (field_type_name == "number"):
                form = ValidateNumberFieldForm(data=data)
                throwInvalideDataException(form)

            if(field_type_name == "float"):
                form = ValidateFloatFieldForm(data=data)
                throwInvalideDataException(form)

            if(field_type_name == "date"):
                form = ValidateDateFieldForm(data=data)
                throwInvalideDataException(form)

            if(field_type_name == "date-time"):
                form = ValidateDateTimeFieldForm(data=data)
                throwInvalideDataException(form)

            if(field_type_name == "duration"):
                form = ValidateDurationFieldForm(data=data)
                throwInvalideDataException(form)

            if(field_type_name == "time"):
                form = ValidateTimeFieldForm(data=data)
                throwInvalideDataException(form)

            if(field_type_name == "image"):
                form = ValidateImageFieldForm(data=data)
                throwInvalideDataException(form)

            if(field_type_name == "file"):
                form = ValidateImageFieldForm(data=data)
                throwInvalideDataException(form)
            
            if (field_type_name in valide_choices_fields):
                choices = field.choices.all()
                form = ValidateChoicesFieldForm(data=data,choices=choices)
                throwInvalideDataException(form)
            
        except  KeyError as e:
            Exception("Invalide Data")

        



def throwInvalideDataException(form):
    if form.is_valid() ==  False:
        raise Exception("Invalide data")

