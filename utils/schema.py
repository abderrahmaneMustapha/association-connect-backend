import graphene
from graphene_file_upload.scalars import Upload

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