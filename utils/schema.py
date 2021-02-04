import graphene
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required

class ImageType(graphene.ObjectType):
    image = Upload()

class SendImageToStorageMutation(graphene.Mutation):
    class Arguments:
        image = Upload()
    
    data =  graphene.String()
    success = graphene.Boolean()

    def mutate(root, info, image):
        print(image)
    
        return SendImageToStorageMutation(data="", success=True)

class UtilsMutations(graphene.ObjectType):
    send_image_to_storage = SendImageToStorageMutation.Field()