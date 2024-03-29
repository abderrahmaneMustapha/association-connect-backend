from graphene_django import DjangoObjectType
import graphene
from graphql_jwt.decorators import login_required
from graphql import GraphQLError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from guardian.shortcuts import assign_perm, remove_perm

from .models import (BaseUser, Member, Association, AssociationGroup,
                     AssociationGroupMember, AssociationType as
                     AssociationTypeModel, ExpectedAssociationMembersNumber)

from .utils import have_association_permission, have_group_permission
from django.contrib.postgres.search import SearchVector
from utils.utils import excludNullFields

#types
class ModelsContentType(DjangoObjectType):
    class Meta:
        model = ContentType
        fields = '__all__'


class ModelsPermissionType(DjangoObjectType):
    class Meta:
        model = Permission
        fields = ['id', 'codename', 'name']


class BaseUserType(DjangoObjectType):
    class Meta:
        model = BaseUser
        fields = '__all__'


class MemberType(DjangoObjectType):
    class Meta:
        model = Member
        fields = ['id', 'association', 'user', 'is_owner']


class AssociationType(DjangoObjectType):
    class Meta:
        model = Association
        fields = [
            'id', 'slug', 'name', 'description', 'association_type',
            'association_min_max_numbers'
        ]


class AssociationGroupType(DjangoObjectType):
    class Meta:
        model = AssociationGroup
        fields = ['id', 'name', 'association', 'group_type']


class AssociationGroupMemberType(DjangoObjectType):
    class Meta:
        model = AssociationGroupMember
        fields = ['member', 'group']


#end types

# inputs 
class UserInputs(graphene.InputObjectType):
    username = graphene.String(required=False)
    first_name = graphene.String(required=False)
    last_name = graphene.String(required=False)
    email = graphene.String(required=True)
    date_birth = graphene.Date(required=False)
    phone = graphene.String(required=False)
    description = graphene.String(required=False)
    adress = graphene.String(required=False)
    city = graphene.String(required=False)
    country = graphene.String(required=False)
class AssociationUpdateInputs(graphene.InputObjectType):
    slug = graphene.String(required=True)
    name = graphene.String(required=False)
    description = graphene.String(required=False)
    association_type = graphene.ID(required=False)
    email = graphene.String(required=False)
    phone = graphene.String(required=False)
    association_min_max_numbers = graphene.ID(required=False)
# mutations

class UpdateUserInfoMutation(graphene.Mutation):
    class Arguments : 
        inputs = UserInputs()
    
    success = graphene.Boolean()
    user = graphene.Field(BaseUserType)
    
    @login_required
    def mutate(root, info, inputs):
        values = excludNullFields(inputs, 'email')

        user = BaseUser.objects.filter(email=inputs.email)
        user_exists  = user.exists()
        success = False
        returned_user = None

        if user_exists and info.context.user.email == inputs.email:            
            user.update(**values)
            returned_user= user.first()
            success=True

        return UpdateUserInfoMutation(success=success, user=returned_user)

class UpdateAssociationInfoMutation(graphene.Mutation):
    class Arguments:
        inputs = AssociationUpdateInputs()
    
    success = graphene.Boolean()
    association = graphene.Field(AssociationType)

    def mutate(root, info, inputs):
        values = excludNullFields(inputs, "slug")

        association = Association.objects.filter(slug=inputs.slug)
        
        association_exists = association.exists()

        association_returned  = None
        success = False

        if association_exists : 
        
            if  have_association_permission(association.first() , info.context.user,
                                        "update_association_info"):
                success=True
                association.update(**values)
                association_returned = association.first()
            
        return UpdateAssociationInfoMutation(success=success, association=association_returned)
class MemberAddByAdminMutation(graphene.Mutation):
    class Arguments:
        association = graphene.ID()
        user = graphene.String()

    success = graphene.Boolean()
    member = graphene.Field(MemberType)

    @login_required
    def mutate(root, info, association, user):

        association = Association.objects.get(id=association)
        member = None
        success = True
        if have_association_permission(association, info.context.user,
                                       "add_association_member"):
            user_ = BaseUser.objects.get(key=user)
            member = Member.objects.create(association=association, user=user_)
        else:
            success = False

        return MemberAddByAdminMutation(member=member, success=success)


class MemberDeleteMutation(graphene.Mutation):
    class Arguments:
        user = graphene.String()
        association = graphene.ID()

    success = graphene.Boolean()
    member = graphene.Field(MemberType)

    @login_required
    def mutate(root, info, association, user):
        _association = Association.objects.get(id=association)
        member = None
        success = False
        if have_association_permission(_association, info.context.user,
                                       "delete_association_member"):
            member = Member.objects.filter(association=_association,
                                           user__key=user).delete()
            success = True

        return MemberDeleteMutation(member=member, success=success)


class MemberArchiveMutation(graphene.Mutation):
    class Arguments:
        user = graphene.String()
        association = graphene.ID()

    success = graphene.Boolean()
    member = graphene.Field(MemberType)

    @login_required
    def mutate(root, info, association, user):
        _association = Association.objects.get(id=association)
        success = False
        member = None
        if have_association_permission(_association, info.context.user,
                                       "delete_association_member"):
            member = Member.objects.get(association=_association,
                                        user__key=user)
            member.is_archived = True
            member.save()
            success = True

        return MemberArchiveMutation(member=member, success=success)


class AssociationCreationMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        description = graphene.String()
        association_type = graphene.ID()
        association_min_max_numbers = graphene.ID()
        phone = graphene.String()
        email = graphene.String()

    success = graphene.Boolean()
    association = graphene.Field(AssociationType)

    @login_required
    def mutate(root, info, name, description, association_type,
               association_min_max_numbers, phone, email):

        association_type = AssociationTypeModel.objects.get(
            id=association_type)

        association_min_max_numbers = ExpectedAssociationMembersNumber.objects.get(
            id=association_min_max_numbers)

        association = Association.objects.create(
            name=name,
            phone=phone,
            email=email,
            description=description,
            association_type=association_type,
            association_min_max_numbers=association_min_max_numbers)

        association.slugify_()
        association.full_clean()
        association.save()

        user = info.context.user
        user.is_association_owner = True
        user.save()

        Member.objects.create(user=user,
                              association=association,
                              is_owner=True)

        success = True

        return AssociationCreationMutation(association=association,
                                           success=success)


# when a user try to create an association by clicking on the start
# a free trial  button on the home page
class AssociationCreationNoRegisterMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        association_type = graphene.ID()
        phone = graphene.String()
        email = graphene.String()

    success = graphene.Boolean()
    association = graphene.Field(AssociationType)

    def mutate(root, info, name, email, association_type, phone):

        association_type = AssociationTypeModel.objects.get(
            id=association_type)

        association = Association.objects.create(
            phone=phone,
            email=email,
            name=name,
            association_type=association_type)

        association.slugify_()
        association.save()
        user = info.context.user
        user.is_association_owner = True
        user.phone = phone
        user.save()

        Member.objects.create(user=user,
                              association=association,
                              is_owner=True)

        success = True

        return AssociationCreationMutation(association=association,
                                           success=success)


class AssociationDeleteMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    success = graphene.Boolean()
    association = graphene.Field(AssociationType)

    @login_required
    def mutate(root, info, id):
        super_member = Member.objects.filter(
            user=info.context.user, association__id=id).first().is_owner
        association_ = None
        success = False
        if super_member:
            association = Association.objects.filter(id=id)
            association_ = association.first()
            association.delete()
            success = True

        return AssociationDeleteMutation(association=association_,
                                         success=success)


class AssociationUpdateDescriptionMutation(graphene.Mutation):
    class Arguments:
        association = graphene.ID()
        description = graphene.String()

    success = graphene.Boolean()
    association = graphene.Field(AssociationType)

    @login_required
    def mutate(root, info, association, description):
        association = Association.objects.get(id=association)
        success = False
        if have_association_permission(association, info.context.user,
                                       "update_association_info"):
            association.description = description
            association.save()
            success = True
        return AssociationCreationMutation(association=association,
                                           success=success)


class AssociationGroupCreationMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        association = graphene.ID()
        group_type = graphene.String()

    success = graphene.Boolean()
    group = graphene.Field(AssociationGroupType)

    @login_required
    def mutate(root, info, name, association, group_type):
        _association = Association.objects.get(id=association)
        _group = None
        success = False
        if have_association_permission(_association, info.context.user,
                                       "manage_group"):
            _group = AssociationGroup.objects.create(name=name,
                                                     association=_association,
                                                     group_type=group_type)
            success = True
        return AssociationGroupCreationMutation(group=_group, success=success)


class AssociationGroupDeleteMutation(graphene.Mutation):
    class Arguments:
        group = graphene.ID()
        association = graphene.ID()

    success = graphene.Boolean()
    group = graphene.Field(AssociationGroupType)

    @login_required
    def mutate(root, info, group, association):

        _association = Association.objects.get(id=association)
        _group = None
        success = False
        if have_association_permission(_association, info.context.user,
                                       "manage_group"):
            _group = AssociationGroup.objects.filter(id=group,
                                                     association=_association)
            _group.delete()
            _group = _group.first()
            success = True
        return AssociationGroupCreationMutation(group=_group, success=success)


class AssociationGroupMemberAddMutation(graphene.Mutation):
    class Arguments:
        member = graphene.ID()
        group = graphene.ID()

    success = graphene.Boolean()
    member = graphene.Field(AssociationGroupMemberType)

    @login_required
    def mutate(root, info, member, group):
        _member = Member.objects.get(id=member)
        _group = AssociationGroup.objects.get(id=group)
      
        group_member = None
        success = False

        if have_group_permission(_group.association, _group, info.context.user,
                                 "add_group_member") :
            
            group_member = AssociationGroupMember.objects.create(
                member=_member, group=_group)
            success = True
        return AssociationGroupMemberAddMutation(member=group_member,
                                                 success=success)


class AssociationGroupMemberRemoveMutation(graphene.Mutation):
    class Arguments:
        member = graphene.ID()
        group = graphene.ID()

    success = graphene.Boolean()
    member = graphene.Field(AssociationGroupMemberType)

    @login_required
    def mutate(root, info, member, group):
        _group = AssociationGroup.objects.get(id=group)
        success = False
        group_member = None
        if have_group_permission(_group.association, _group, info.context.user,
                                 "delete_group_member"):
            group_member = AssociationGroupMember.objects.filter(
                member__id=member, group=_group)
            group_member.delete()
            success = True
        return AssociationGroupMemberRemoveMutation(
            member=group_member.first(), success=success)


class OwnerGiveAssociationPermissionsToMembers(graphene.Mutation):
    class Arguments:
        permission = graphene.String()
        association = graphene.ID()
        member = graphene.ID()

    success = graphene.Boolean()
    member = graphene.Field(MemberType)

    @login_required
    def mutate(root, info, permission, association, member):
        _association = Association.objects.get(id=association)
        _member = Member.objects.get(id=member)
        success = False
        if have_association_permission(_association, info.context.user,
                                       "manage_association_permissions"):
            assign_perm(permission, _member.user, _association)
            success = True
        return OwnerGiveAssociationPermissionsToMembers(member=_member,
                                                        success=success)


class OwnerRemoveAssociationPermissionsToMembers(graphene.Mutation):
    class Arguments:
        permission = graphene.String()
        association = graphene.ID()
        member = graphene.ID()

    success = graphene.Boolean()
    member = graphene.Field(MemberType)

    @login_required
    def mutate(root, info, permission, association, member):
        _association = Association.objects.get(id=association)
        _member = Member.objects.get(id=member)
        success = False
        if have_association_permission(_association, info.context.user,
                                       "manage_association_permissions"):
            remove_perm(permission, _member.user, _association)
            success = True
        return OwnerRemoveAssociationPermissionsToMembers(member=_member,
                                                          success=success)


class OwnerGiveGroupPermissionsToMembers(graphene.Mutation):
    class Arguments:
        permission = graphene.String()
        association = graphene.ID()
        group = graphene.ID()
        member = graphene.ID()

    success = graphene.Boolean()
    member = graphene.Field(MemberType)

    @login_required
    def mutate(root, info, permission, association, group, member):
        _association = Association.objects.get(id=association)
        _group = AssociationGroup.objects.get(id=group,
                                              association__id=association)
        success = False
        _member = None
        if have_group_permission(_group.association, _group, info.context.user,
                                 "manage_group_permissions"):
            _member = Member.objects.get(id=member)
            assign_perm(permission, _member.user, _group)
            success = True
        return OwnerGiveGroupPermissionsToMembers(member=_member,
                                                  success=success)


class OwnerRemoveGroupPermissionsToMembers(graphene.Mutation):
    class Arguments:
        permission = graphene.String()
        association = graphene.ID()
        group = graphene.ID()
        member = graphene.ID()

    success = graphene.Boolean()
    member = graphene.Field(MemberType)

    @login_required
    def mutate(root, info, permission, association, group, member):
        _association = Association.objects.get(id=association)
        _group = AssociationGroup.objects.get(id=group,
                                              association__id=association)

        success = False
        _member = None
        if have_group_permission(_group.association, _group, info.context.user,
                                 "manage_group_permissions"):
            _member = Member.objects.get(id=member)
            remove_perm(permission, _member.user, _group)
            success = True
        return OwnerRemoveGroupPermissionsToMembers(member=_member,
                                                    success=success)


# end mutations
class AccountsMutation(graphene.ObjectType):
    add_memeber_by_admin = MemberAddByAdminMutation.Field()
    delete_member = MemberDeleteMutation.Field()
    archive_member = MemberArchiveMutation.Field()
    update_association_info  = UpdateAssociationInfoMutation.Field()
    update_user_info = UpdateUserInfoMutation.Field()
    create_association = AssociationCreationMutation.Field()
    create_association_no_register = AssociationCreationNoRegisterMutation.Field(
    )
    update_association_description = AssociationUpdateDescriptionMutation.Field(
    )
    delete_assciation = AssociationDeleteMutation.Field()

    create_group = AssociationGroupCreationMutation.Field()
    delete_group = AssociationGroupDeleteMutation.Field()

    add_member_group = AssociationGroupMemberAddMutation.Field()
    remove_member_group = AssociationGroupMemberRemoveMutation.Field()

    #permissions
    give_member_association_permission = OwnerGiveAssociationPermissionsToMembers.Field(
    )
    remove_member_association_permission = OwnerRemoveAssociationPermissionsToMembers.Field(
    )
    give_member_group_permission = OwnerGiveGroupPermissionsToMembers.Field()
    remove_member_group_permission = OwnerRemoveGroupPermissionsToMembers.Field(
    )


class AccountsQuery(graphene.ObjectType):
    get_association_by_slug = graphene.Field(
        AssociationType, slug=graphene.String(required=True))

    get_all_associations = graphene.List(AssociationType,
                                         query=graphene.String(required=False))

    get_associations_group_by_id = graphene.Field(
        AssociationGroupType, id=graphene.ID(required=True))
    get_all_associations_groups = graphene.List(
        AssociationGroupType, slug=graphene.String(required=True))
    get_all_associations_dynamique_groups = graphene.List(
        AssociationGroupType, slug=graphene.String(required=True))
    get_all_associations_statique_groups = graphene.List(
        AssociationGroupType, slug=graphene.String(required=True))
    get_associations_members = graphene.List(
        MemberType, slug=graphene.String(required=True))
    get_association_member_by_id = graphene.Field(
        MemberType, id=graphene.ID(required=True))

    get_all_association_object_permissions = graphene.List(
        ModelsPermissionType)

    get_all_association_group_object_permissions = graphene.List(
        ModelsPermissionType)

    get_all_association_member_object_permissions = graphene.List(
        ModelsPermissionType)

    get_all_association_group_member_object_permissions = graphene.List(
        ModelsPermissionType)


    def resolve_get_association_by_slug(root, info, slug):
        return Association.objects.get(slug=slug, block=False)

    @login_required
    def resolve_get_all_associations(root, info, query=None):
        if query:
            return Association.objects.annotate(
                search=SearchVector('name', 'description')).filter(
                    search__icontains=query, block=False)
        else:
            return Association.objects.filter(block=False)

    @login_required
    def resolve_get_all_associations_statique_groups(root, info, slug):
        member = Member.objects.filter(user=info.context.user,
                                       association__slug=slug).first()

        if have_association_permission(member.association, member.user,
                                       'manage_group'):
            return AssociationGroup.objects.filter(association__slug=slug,
                                                   group_type="S")
        else:
            return None

    @login_required
    def resolve_get_all_associations_dynamique_groups(root, info, slug):
        return AssociationGroup.objects.filter(association__slug=slug,
                                               group_type="D")

    @login_required
    def resolve_get_all_associations_groups(root, info, slug):
        member = Member.objects.get(user=info.context.user,
                                    association__slug=slug)
        if have_association_permission(member.association, member.user,
                                       'manage_group'):
            return AssociationGroup.objects.filter(association__slug=slug)
        else:
            return None

    @login_required
    def resolve_get_associations_group_by_id(root, info, id):
        group = AssociationGroup.objects.get(pk=id)
        member = Member.objects.filter(user=info.context.user,
                                       association=group.association).count()
        if member == 1:
            return group
        else:
            return None

    @login_required
    def resolve_get_associations_members(root, info, slug):
        member = Member.objects.filter(association__slug=slug)
        if have_association_permission(member.first().association,
                                       member.first().user,
                                       "view_association_member"):
            return member
        else:
            return None

    @login_required
    def resolve_get_association_member_by_id(root, info, id):
        member = Member.objects.filter(id=id)
        super_member = Member.objects.get(
            user=info.context.user, association=member.first().association)
        if member.exists() or have_association_permission(
                super_member.association, super_member.user,
                "view_association_member"):
            return member.first()
        else:
            return None

    @login_required
    def resolve_get_all_association_object_permissions(root, info):
        content_type = ContentType.objects.get_for_model(Association)
        return Permission.objects.filter(content_type=content_type)

    @login_required
    def resolve_get_all_association_group_object_permissions(root, info):
        content_type = ContentType.objects.get_for_model(AssociationGroup)
        return Permission.objects.filter(content_type=content_type)

    @login_required
    def resolve_get_all_association_member_object_permissions(root, info):
        content_type = ContentType.objects.get_for_model(Member)
        return Permission.objects.filter(content_type=content_type)

    @login_required
    def resolve_get_all_association_group_member_object_permissions(
            root, info):
        content_type = ContentType.objects.get_for_model(
            AssociationGroupMember)
        return Permission.objects.filter(content_type=content_type)
