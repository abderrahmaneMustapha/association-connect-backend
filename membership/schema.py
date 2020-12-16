from graphene_django import DjangoObjectType
import graphene
from .models import Form, Association, Costs, UserPayedCosts, BaseUser, Field, FieldType, FieldData


class FormMetaType(DjangoObjectType):
    class Meta:
        model = Form
        fields = [
            'id', 'association', 'title', 'description', 'email', 'start_date',
            'days'
        ]


class CostType(DjangoObjectType):
    class Meta:
        model = Costs
        fields = [
            'id', 'form', 'description', 'amount', 'membership_time',
            'show_in_form'
        ]


class UserPayedCostType(DjangoObjectType):
    class Meta:
        model = UserPayedCosts
        fields = ['id', 'cost', 'user']


class FormFieldType(DjangoObjectType):
    class Meta:
        model = Field
        fields = [
            'id', 'label', 'description', 'placeholder', 'show_in_form',
            'required', 'type'
        ]

class FieldDataType(DjangoObjectType):
    class Meta:
        model = FieldData
        fields = ['id', 'field', 'user', 'data']
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
        _form.full_clean()
        success = True
        return FormMetaAddMutation(form=_form, success=success)


class AddCostMutation(graphene.Mutation):
    class Arguments:
        form = graphene.ID()
        description = graphene.String()
        amount = graphene.Float()
        membership_time = graphene.String()
        show_in_form = graphene.Boolean()

    cost = graphene.Field(CostType)
    success = graphene.Boolean()

    def mutate(root, info, form, description, amount, membership_time,
               show_in_form):
        _form = Form.objects.get(id=form)
        cost = Costs.objects.create(form=_form,
                                    description=description,
                                    amount=amount,
                                    membership_time=membership_time,
                                    show_in_form=show_in_form)
        cost.full_clean()
        success = True
        return AddCostMutation(cost=cost, success=success)


class AddUserPayedCostMutation(graphene.Mutation):
    class Arguments:
        cost = graphene.ID()
        user = graphene.String()

    cost = graphene.Field(UserPayedCostType)
    success = graphene.Boolean()

    def mutate(root, info, cost, user):
        _cost = Costs.objects.get(id=cost)
        _user = BaseUser.objects.get(pk=user)
        user_payed_cost = UserPayedCosts.objects.create(cost=_cost, user=_user)
        user_payed_cost.full_clean()
        success = True
        return AddUserPayedCostMutation(cost=user_payed_cost, success=success)


class AddFormFieldMutation(graphene.Mutation):
    class Arguments:
        form = graphene.ID()
        label = graphene.String()
        description = graphene.String()
        placeholder = graphene.String()
        show_in_form = graphene.Boolean()
        required = graphene.Boolean()
        type = graphene.ID()

    field = graphene.Field(FormFieldType)
    success = graphene.Boolean()

    def mutate(root, info, form, label, description, placeholder, show_in_form,
               required, type):
        _form = Form.objects.get(pk=form)
        _field_type = FieldType.objects.get(id=type)
        _field = Field.objects.create(form=_form,
                                      label=label,
                                      description=description,
                                      placeholder=placeholder,
                                      show_in_form=show_in_form,
                                      required=required,
                                      type=_field_type)
        success  = True

        return AddFormFieldMutation(field=_field, success=success)

class AddFieldData(graphene.Mutation):
    class Arguments:
        field = graphene.ID()
        user =  graphene.String()
        data = graphene.JSONString()
    
    data = graphene.Field(FieldDataType)
    success = graphene.Boolean()
    def mutate(root, info, field, user, data):
        _user = BaseUser.objects.get(pk=user)
        _field = Field.objects.get(pk=field)

        data = FieldData.objects.create(field=_field, user=_user, data=data)
        return AddFieldData(data=data, success=success)
        
#global query and mutations
class MembershipMutation(graphene.ObjectType):
    add_form_meta = FormMetaAddMutation.Field()
    add_cost_to_form = AddCostMutation.Field()
    add_user_payed_costs = AddUserPayedCostMutation.Field()
    add_field_to_form = AddFormFieldMutation.Field()

class MembershipQuery(graphene.ObjectType):
    get_form_meta = graphene.Field(FormMetaType, id=graphene.ID())

    def resolve_get_form_meta(root, info, id):
        return Form.objects.get(id=id)
