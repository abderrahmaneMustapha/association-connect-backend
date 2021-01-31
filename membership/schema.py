from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from django.core.exceptions import ValidationError
import graphene
from accounts.models import AssociationGroupMember
from accounts.schema import BaseUserType, MemberType
from .models import Form, AssociationGroupJoinRequest, Association, JoinRequest, Member, AssociationMembership, Costs, UserPayedCosts, BaseUser, Field, FieldType, FieldData, FormFilledByUser, AssociationGroup
from accounts.utils import have_association_permission
from django.template.defaultfilters import slugify


# object types
class FormMetaType(DjangoObjectType):
    class Meta:
        model = Form
        fields = [
            'id', 'association', 'title', 'description', 'email', 'start_date',
            'days', 'add_to_request', 'link', 'photo', 'phone_number'
        ]


class FieldTypeType(DjangoObjectType):
    class Meta:
        model = FieldType
        fields = ['name']


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
        fields = ['user_payed_cost']


class JoinRequestType(DjangoObjectType):
    class Meta:
        model = JoinRequest
        fields = ['user_payed_cost']


#inputs
class FormCostsInputs(graphene.InputObjectType):
    association_slug = graphene.String()
    title = graphene.String()
    description = graphene.String()
    amount = graphene.Float()
    membership_time = graphene.String()
    show_in_form = graphene.Boolean()


class FormFieldsInputs(graphene.InputObjectType):
    association_slug = graphene.String()
    label = graphene.String()
    description = graphene.String()
    placeholder = graphene.String()
    show_in_form = graphene.Boolean()
    required = graphene.Boolean()
    type = graphene.String()


#mutations


class FormMetaAddMutation(graphene.Mutation):
    class Arguments:
        association = graphene.ID()
        title = graphene.String()
        description = graphene.String()
        email = graphene.String()
        phone = graphene.String()
        photo = Upload(required=False)
        link = graphene.String(required=False)
        start_date = graphene.Date()
        days = graphene.Int()
        add_to_request = graphene.Boolean(required=False)

    form = graphene.Field(FormMetaType)
    success = graphene.Boolean()

    def mutate(root,
               info,
               association,
               title,
               description,
               email,
               phone,
               start_date,
               days,
               photo=None,
                link=None,
               add_to_request=False):

        _association = Association.objects.get(id=association)
        success = False
        _association_form = None

        if have_association_permission(association=_association,
                                       user=info.context.user,
                                       permission="manage_association_form"):
            _association_form = Form.objects.filter(association=_association)
            _association_form_exists = _association_form.exists()

            if _association_form_exists:
                Form.objects.filter(association=_association).update(
                    title=title,
                    description=description,
                    email=email,
                    photo=photo,
                    phone_number=phone,
                    link=link,
                    start_date=start_date,
                    days=days)
                _association_form = _association_form.first()
                success = True
            else:
                _association_form = Form.objects.create(
                    association=_association,
                    title=title,
                    description=description,
                    email=email,
                    photo=photo,
                    phone_number=phone,
                    link=link,
                    start_date=start_date,
                    days=days)
                success = True

        _association_form.full_clean()

        return FormMetaAddMutation(form=_association_form, success=success)


class AddCostsMutation(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(FormCostsInputs)

    cost = graphene.List(CostType)
    success = graphene.Boolean()

    def mutate(root, info, inputs):
        _form = Form.objects.filter(
            association__slug=inputs[0].association_slug).first()
       

        success = False
        costs = []

        if have_association_permission(association=_form.association,
                                       user=info.context.user,
                                       permission="manage_association_form"):
            Costs.objects.filter(form=_form).delete()
            for _input in inputs:
                cost = Costs.objects.create(
                    title =_input.title,
                    form=_form,
                    description=_input.description,
                    amount=_input.amount,
                    membership_time=_input.membership_time,
                    show_in_form=_input.show_in_form)

                cost.full_clean()
                costs.append(cost)

            success = True
        return AddCostsMutation(cost=costs, success=success)


class AddCostMutation(graphene.Mutation):
    class Arguments:
        inputs = FormCostsInputs(required=True)

    cost = graphene.Field(CostType)
    success = graphene.Boolean()

    def mutate(root, info, inputs):

        _form = Form.objects.filter(
            association__slug=inputs.association_slug).first()
        success = False

        if have_association_permission(association=_form.association,
                                       user=info.context.user,
                                       permission="manage_association_form"):
            Costs.objects.filter(form=_form).delete()

            cost = Costs.objects.create(
                title =inputs.title,
                form=_form,
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
    user = graphene.Field(BaseUserType)

    def mutate(root, info, cost, user):
        _cost = Costs.objects.get(id=cost)
        _user = BaseUser.objects.get(pk=user)
        user_payed_cost = UserPayedCosts.objects.create(cost=_cost, user=_user)
        user_payed_cost.full_clean()
        success = True
        return AddUserPayedCostMutation(cost=user_payed_cost,
                                        user=_user,
                                        success=success)


class AddFormFieldsMutation(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(FormFieldsInputs)

    fields = graphene.List(FormFieldType)
    success = graphene.Boolean()

    def mutate(root, info, inputs):
        _form = Form.objects.filter(
            association__slug=inputs[0].association_slug).first()
        _fields = []
        success = False
        if have_association_permission(association=_form.association,
                                       user=info.context.user,
                                       permission="manage_association_form"):

            Field.objects.filter(form=_form).delete()

            for _input in inputs:
                _field_type = FieldType.objects.get(name=_input.type)
                _field = Field.objects.create(form=_form,
                                              label=_input.label,
                                              name=slugify(_input.label),
                                              description=_input.description,
                                              placeholder=_input.placeholder,
                                              show_in_form=_input.show_in_form,
                                              required=_input.required,
                                              type=_field_type)

                _field.full_clean()
                _fields.append(_field)
            success = True

        return AddFormFieldsMutation(fields=_fields, success=success)


class AddFormFieldMutation(graphene.Mutation):
    class Arguments:
        inputs = FormFieldsInputs(True)

    field = graphene.Field(FormFieldType)
    success = graphene.Boolean()

    def mutate(root, info, inputs):
        _form = Form.objects.filter(
            association__slug=inputs.association_slug).first()

        success = False
        _field = None

        if have_association_permission(association=_form.association,
                                       user=info.context.user,
                                       permission="manage_association_form"):

            _field_type = FieldType.objects.get(name=inputs.type)
            Field.objects.filter(form=_form).delete()
            _field = Field.objects.create(form=_form,
                                          label=inputs.label,
                                          name=slugify(inputs.label),
                                          description=inputs.description,
                                          placeholder=inputs.placeholder,
                                          show_in_form=inputs.show_in_form,
                                          required=inputs.required,
                                          type=_field_type)
            _field.full_clean()
            success = True

        return AddFormFieldMutation(field=_field, success=success)


class AddFieldData(graphene.Mutation):
    class Arguments:
        field = graphene.ID()
        user = graphene.String()
        data = graphene.String()

    data = graphene.Field(FieldDataType)
    success = graphene.Boolean()

    def mutate(root, info, field, user, data):
        _user = BaseUser.objects.get(pk=user)
        _field = Field.objects.get(pk=field)
        success = False
        _data = None
        if have_association_permission(association=_field.form.association,
                                       user=info.context.user,
                                       permission="manage_association_form"):

            _data = FieldData.objects.create(field=_field,
                                             user=_user,
                                             data=data)
            _data.full_clean()
            success = True
        return AddFieldData(data=_data, success=success)


class FormFilledByUserMutation(graphene.Mutation):
    class Arguments:
        user_payed_cost = graphene.ID()
        groups = graphene.List(graphene.ID, required=False)

    filled_form = graphene.Field(FormFilledType)
    success = graphene.Boolean()

    def mutate(root, info, user_payed_cost, groups=[]):

        _user_payed_cost = UserPayedCosts.objects.get(id=user_payed_cost)

        _form_filled = FormFilledByUser.objects.create(
            user_payed_cost=_user_payed_cost)
        _form_filled.full_clean()

        add_to_request = _user_payed_cost.cost.form.add_to_request
        if add_to_request:
            for group_id in groups:
                group = AssociationGroup.objects.get(id=group_id)
                AssociationGroupJoinRequest.objects.create(
                    group=group, user_payed_cost=_user_payed_cost)
        else:
            for group_id in groups:
                member = Member.objects.get(
                    user=_user_payed_cost.user,
                    association=_user_payed_cost.cost.form.association)
                group = AssociationGroup.objects.get(id=group_id)
                AssociationGroupMember.objects.create(member=member,
                                                      group=group)
        success = True

        return FormFilledByUserMutation(filled_form=_form_filled,
                                        success=success)


class AcceptJoinRequestMutation(graphene.Mutation):
    class Arguments:
        join_request = graphene.ID()

    success = graphene.Boolean()
    join_request = graphene.Field(JoinRequestType)
    member = graphene.Field(MemberType)

    def mutate(root, info, join_request):
        _join_request = JoinRequest.objects.get(id=join_request)
        success = False
        member = None
        if have_association_permission(association=_join_request.
                                       user_payed_cost.cost.form.association,
                                       user=info.context.user,
                                       permission="add_association_member"):
            success = True
            _join_request.accept = True
            _join_request.save()
            member = Member.objects.create(
                user=_join_request.user_payed_cost.user,
                association=_join_request.user_payed_cost.cost.form.association
            )
            AssociationMembership.objects.create(
                membership_time=_join_request.user_payed_cost.cost.
                membership_time,
                member=member)

            groups_join_reqs = AssociationGroupJoinRequest.objects.filter(
                user_payed_cost=_join_request.user_payed_cost)
            for group_joi_req in groups_join_reqs:
                AssociationGroupMember.objects.create(
                    member=member, group=group_joi_req.group)

        return AcceptJoinRequestMutation(success=success,
                                         member=member,
                                         join_request=join_request)


class DeclineJoinRequestMutation(graphene.Mutation):
    class Arguments:
        join_request_id = graphene.ID()

    join_request = graphene.Field(JoinRequestType)
    success = graphene.Boolean()

    def mutate(root, info, join_request_id):
        _join_request = JoinRequest.objects.filter(id=join_request_id)
        success = False
        if have_association_permission(association=_join_request.first().
                                       user_payed_cost.cost.form.association,
                                       user=info.context.user,
                                       permission="delete_association_member"):
            _join_request.delete()
            _join_request = _join_request.first()
            success = True

        return DeclineJoinRequestMutation(success=success,
                                          join_request=_join_request)


#global query and mutations
class MembershipMutation(graphene.ObjectType):
    add_form_meta = FormMetaAddMutation.Field()
    add_costs_to_form = AddCostsMutation.Field()
    add_cost_to_form = AddCostMutation.Field()
    add_user_payed_costs = AddUserPayedCostMutation.Field()
    add_fields_to_form = AddFormFieldsMutation.Field()
    add_field_to_form = AddFormFieldMutation.Field()
    add_data_to_field = AddFieldData.Field()
    form_filled = FormFilledByUserMutation.Field()
    accept_join_request = AcceptJoinRequestMutation.Field()
    decline_join_request = DeclineJoinRequestMutation.Field()


class MembershipQuery(graphene.ObjectType):
    get_form_meta = graphene.Field(FormMetaType, id=graphene.ID())
    get_form_by_association_slug = graphene.Field(FormMetaType,
                                                  slug=graphene.String())

    get_form_field_type = graphene.List(FieldTypeType)

    get_form_showed_fields = graphene.List(FormFieldType,
                                           slug=graphene.String())
    get_form_all_fields = graphene.List(FormFieldType, slug=graphene.String())

    get_form_all_fields_data = graphene.List(FieldDataType,
                                             form_id=graphene.ID())
    get_form_showed_fields_data = graphene.List(FieldDataType,
                                                form_id=graphene.ID())
    get_form_all_fields_user_data = graphene.List(FieldDataType,
                                                  form_id=graphene.ID(),
                                                  key=graphene.String())

    get_form_all_costs = graphene.List(CostType, slug=graphene.String())
    get_form_showed_costs = graphene.List(CostType, slug=graphene.String())

    get_association_form_filled = graphene.List(FormFilledType,
                                                slug=graphene.String())
    get_association_form_filled_by_user = graphene.List(FormFilledType,
                                                        slug=graphene.String(),
                                                        key=graphene.String())

    get_user_association_payed_costs = graphene.List(UserPayedCostType,
                                                     slug=graphene.String())

    get_user_accepted_join_request = graphene.List(JoinRequestType,
                                                   slug=graphene.String())
    get_user_declined_join_request = graphene.List(JoinRequestType,
                                                   slug=graphene.String())
    get_user_all_join_request = graphene.List(JoinRequestType,
                                              slug=graphene.String())

    def resolve_get_form_meta(root, info, id):
        return Form.objects.get(id=id)

    def resolve_get_form_by_association_slug(root, info, slug):
        member = Member.objects.get(user=info.context.user, association__slug=slug)
        if  have_association_permission(
                member.association, member.user, "manage_association_form"):

            return Form.objects.filter(association__slug=slug).first()

        else:

            return None

    def resolve_get_form_showed_fields(root, info, slug):
        member = Member.objects.get(user=info.context.user, association__slug=slug)
        if have_association_permission(
                member.association, member.user, "manage_association_form"):
            return Field.objects.filter(form__association__slug=slug,
                                       show_in_form=True)
        else:
            return None

    def resolve_get_form_all_fields(root, info, slug):
        member = Member.objects.get(user=info.context.user, association__slug=slug)

        if have_association_permission(
                member.association, member.user, "manage_association_form"):
            return Field.objects.filter(form__association__slug=slug)
        else:
            return None

    def resolve_get_form_showed_fields_data(root, info, form_id):

        return FieldData.objects.filter(field__form__id=form_id,
                                        field__show_in_form=True)

    def resolve_get_form_all_fields_data(root, info, form_id):
        form = Form.objects.get(id=form_id)
        member = Member.objects.get(user=info.context.user, association=form.association)

        if have_association_permission(member.association, member.user,
                                       "manage_association_form"):

            return FieldData.objects.filter(field__form__id=form_id)

        else:
            return None

    def resolve_get_form_all_fields_user_data(root, info, form_id, key):
        form = Form.objects.get(id=form_id)
        member = Member.objects.get(user=info.context.user, association=form.association)
        
        if have_association_permission(member.association, member.user,
                                       "manage_association_form"):
            return FieldData.objects.filter(field__form__id=form_id, user__key=key)
        else:
            return None

    def resolve_get_form_all_costs(root, info, slug):
        member = Member.objects.get(user=info.context.user, association__slug=slug)

        if have_association_permission(member.association, member.user,
                                       "manage_association_form"):
            return Costs.objects.filter(form__association__slug=slug)
        else:
            return None

    def resolve_get_form_showed_costs(root, info, slug):
        return Costs.objects.filter(form__association__slug=slug,
                                    show_in_form=True)

    def resolve_get_user_association_payed_costs(root, info, slug):
        member = Member.objects.get(user=info.context.user, association__slug=slug)

        if have_association_permission(member.association, member.user,
                                       "manage_association_payment"):
            return UserPayedCosts.objects.filter(
                cost__form__association__slug=slug)
        else:
            return None

    def resolve_get_form_field_type(root, info):
        return FieldType.objects.all()

    def resolve_get_association_form_filled(root, info, slug):
        member = Member.objects.get(user=info.context.user, association__slug=slug)

        if have_association_permission(member.association, member.user,
                                       "manage_association_form"):
            return FormFilledByUser.objects.filter(
            user_payed_cost__cost__form__association__slug=slug)
        else:
            return None

    def resolve_get_association_form_filled_by_user(root, info, slug, key):
        member = Member.objects.get(user=info.context.user, association__slug=slug)

        if have_association_permission(member.association, member.user,
                                       "manage_association_form"):
            return FormFilledByUser.objects.filter(
                user_payed_cost__cost__form__association__slug=slug,
                user_payed_cost__user__key=key)
        else:
            return None

    def resolve_get_user_accepted_join_request(root, info, slug):
        member = Member.objects.get(user=info.context.user, association__slug=slug)

        if have_association_permission(member.association, member.user,
                                       "add_association_member"):
            return JoinRequest.objects.filter(
                user_payed_cost__cost__form__association__slug=slug, accept=True)
        else:
            return None

    def resolve_get_user_declined_join_request(root, info, slug):
        member = Member.objects.get(user=info.context.user, association__slug=slug)

        if have_association_permission(member.association, member.user,
                                       "add_association_member"):
            return JoinRequest.objects.filter(
                user_payed_cost__cost__form__association__slug=slug, accept=False)
        else:
            return None

    def resolve_get_user_all_join_request(root, info, slug):
        member = Member.objects.get(user=info.context.user, association__slug=slug)

        if have_association_permission(member.association, member.user,
                                       "add_association_member"):
            return JoinRequest.objects.filter(
                user_payed_cost__cost__form__association__slug=slug)
        else:
            return None
