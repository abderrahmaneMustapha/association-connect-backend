from graphene_django import DjangoObjectType
import graphene
from .models import Form, Association, Costs, UserPayedCosts, BaseUser, Field, FieldType, FieldData, FormFilledByUser
from graphene_file_upload.scalars import Upload


# object types
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


class FormFilledType(DjangoObjectType):
    class Meta:
        model = FormFilledByUser
        fields = [ 'user_payed_cost']


#inputs
class FormCostsInputs(graphene.InputObjectType):
    form = graphene.ID()
    description = graphene.String()
    amount = graphene.Float()
    membership_time = graphene.String()
    show_in_form = graphene.Boolean()

class FormFieldsInputs(graphene.InputObjectType):
    form = graphene.ID()
    label = graphene.String()
    description = graphene.String()
    placeholder = graphene.String()
    show_in_form = graphene.Boolean()
    required = graphene.Boolean()
    type = graphene.ID()
#mutations


class FormMetaAddMutation(graphene.Mutation):
    class Arguments:
        association = graphene.ID()
        title = graphene.String()
        description = graphene.String()
        email = graphene.String()
        phone = graphene.String()
        image = Upload()
        link = graphene.String()
        start_date = graphene.Date()
        days = graphene.Int()

    form = graphene.Field(FormMetaType)
    success = graphene.Boolean()

    def mutate(root, info, association, title, description, email, phone, link, start_date,
               days, image=None):
        _association = Association.objects.get(id=association)
        _form = Form.objects.create(association=_association,
                                    title=title,
                                    description=description,
                                    email=email, 
                                    photo=image,
                                    phone_number=phone,
                                    link=link,
                                    start_date=start_date,
                                    days=days)
        _form.full_clean()
        success = True
        return FormMetaAddMutation(form=_form, success=success)


class AddCostsMutation(graphene.Mutation):
    class Arguments:
        inputs = graphene.List( FormCostsInputs)

    cost = graphene.Field(CostType)
    success = graphene.Boolean()

    def mutate(root,info , inputs):
        for _input in inputs:
            _form = Form.objects.get(id=_input.form)
            cost = Costs.objects.create(form=_form,
                                        description=_input.description,
                                        amount=_input.amount,
                                        membership_time=_input.membership_time,
                                        show_in_form=_input.show_in_form)
            cost.full_clean()
        success = True
        return AddCostsMutation(cost=cost, success=success)

class AddCostMutation(graphene.Mutation):
    class Arguments:
        inputs =  FormCostsInputs(required=True)

    cost = graphene.Field(CostType)
    success = graphene.Boolean()

    def mutate(root,info , inputs):
      
        _form = Form.objects.get(id=inputs.form)
        cost = Costs.objects.create(form=_form,
                                    description=inputs.description,
                                    amount=inputs.amount,
                                    membership_time=inputs.membership_time,
                                    show_in_form=inputs.show_in_form)
        cost.full_clean()
        success = True
        return AddCostsMutation(cost=cost, success=success)

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


class AddFormFieldsMutation(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(FormFieldsInputs)

    field = graphene.Field(FormFieldType)
    success = graphene.Boolean()

    def mutate(root, info, inputs):
        for _input in inputs:
            _form = Form.objects.get(pk= _input.form)
            _field_type = FieldType.objects.get(id=_input.type)
            _field = Field.objects.create(form=_form,
                                        label=_input.label,
                                        description=_input.description,
                                        placeholder=_input.placeholder,
                                        show_in_form=_input.show_in_form,
                                        required=_input.required,
                                        type=_field_type)
            _field.full_clean()
        success  = True

        return AddFormFieldMutation(field=_field, success=success)

class AddFormFieldMutation(graphene.Mutation):
    class Arguments:
       inputs = FormFieldsInputs(True)

    field = graphene.Field(FormFieldType)
    success = graphene.Boolean()

    def mutate(root,info, inputs):
        _form = Form.objects.get(pk=inputs.form)
        _field_type = FieldType.objects.get(id=inputs.type)
        _field = Field.objects.create(form=_form,
                                      label=inputs.label,
                                      description=inputs.description,
                                      placeholder=inputs.placeholder,
                                      show_in_form=inputs.show_in_form,
                                      required=inputs.required,
                                      type=_field_type)
        _field.full_clean()
        success  = True

        return AddFormFieldMutation(field=_field, success=success)

class AddFieldData(graphene.Mutation):
    class Arguments:
        field = graphene.ID()
        user =  graphene.String()
        data = graphene.String()
    
    data = graphene.Field(FieldDataType)
    success = graphene.Boolean()
    def mutate(root, info, field, user, data):
        _user = BaseUser.objects.get(pk=user)
        _field = Field.objects.get(pk=field)
    
        _data = FieldData.objects.create(field=_field, user=_user, data=data)
        _data.full_clean()
        success = True
        return AddFieldData(data=_data, success=success)

class FormFilledByUserMutation(graphene.Mutation):
    class Arguments:
        user_payed_cost = graphene.ID()
    
    filled_form = graphene.Field(FormFilledType)
    success = graphene.Boolean()

    def mutate(root, info, user_payed_cost):
     
        _user_payed_cost = UserPayedCosts.objects.get(id=user_payed_cost)
        _form_filled = FormFilledByUser.objects.create( user_payed_cost=_user_payed_cost)
        _form_filled.full_clean()
        success = True

        return FormFilledByUserMutation(filled_form=_form_filled, success=success)

#global query and mutations
class MembershipMutation(graphene.ObjectType):
    add_form_meta = FormMetaAddMutation.Field()
    add_costs_to_form = AddCostsMutation.Field()
    add_cost_to_form = AddCostMutation.Field()
    add_user_payed_costs = AddUserPayedCostMutation.Field()
    add_fields_to_form = AddFormFieldsMutation.Field()
    add_field_to_form = AddFormFieldMutation.Field()
    add_data_to_field = AddFieldData.Field()
    form_filled  = FormFilledByUserMutation.Field()


class MembershipQuery(graphene.ObjectType):
    get_form_meta = graphene.Field(FormMetaType, id=graphene.ID())
    get_form_showed_fields = graphene.List(FormFieldType, form_id = graphene.ID())
    get_form_showed_fields_data = graphene.List(FieldDataType, form_id= graphene.ID())
    get_form_all_fields = graphene.List(FormFieldType, form_id = graphene.ID())
    get_form_all_fields_data = graphene.List(FieldDataType, form_id= graphene.ID())

    def resolve_get_form_meta(root, info, id):
        return Form.objects.get(id=id)
    
    def resolve_get_form_showed_fields(root, info, form_id):
        return Field.objects.filter(form__id=form_id, show_in_form=True)

    def resolve_get_form_showed_fields_data(root, info, form_id):
        return FieldData.objects.filter(form__id=form_id, show_in_form=True)
    
    def resolve_get_form_all_fields(root, info, form_id):
        return Field.objects.filter(form__id=form_id, show_in_form=True)

    def resolve_get_form_all_fields_data(root, info, form_id):
        return FieldData.objects.filter(form__id=form_id, field__show_in_form=True)
