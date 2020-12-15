from graphene_django import DjangoObjectType
import graphene
from .models import Form, Association


class FormMetaType(DjangoObjectType):
    class Meta:
        model = Form
        fields = [
            'id', 'association', 'title', 'description', 'email', 'start_date',
            'days'
        ]


#mutations


class FormMetaAddMutation(graphene.Mutation):
    class Arguments:
        association = graphene.ID()
        title = graphene.String()
        description = graphene.String()
        email = graphene.String()
        start_date = graphene.Date()
        days = graphene.Int()

    form = graphene.Field(FormMetaType)
    success = graphene.Boolean()

    def mutate(root, info, association, title, description, email, start_date,
               days):
        _association = Association.objects.get(id=association)
        _form = Form.objects.create(association=_association,
                                    title=title,
                                    description=description,
                                    email=email,
                                    start_date=start_date,
                                    days=days)
        success = True
        return FormMetaAddMutation(form=_form, success=success)


class MembershipMutation(graphene.ObjectType):
    add_form_meta = FormMetaAddMutation.Field()


class MembershipQuery(graphene.ObjectType):
    get_form_meta = graphene.Field(FormMetaType, id=graphene.ID())

    def resolve_get_form_meta(root, info, id):
        return Form.objects.get(id=id)


