import graphene
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required

class ImageType(graphene.ObjectType):
    image = Upload()

class SendImageToStorageMutation(graphene.Mutation):
    class Arguments:
        image = Upload()
    
    @login_required
    def mutate(root, info, image):
        print(image)


class UtilsMutations(graphene.Mutation):
    send_image_to_storage = SendImageToStorageMutation.Field()