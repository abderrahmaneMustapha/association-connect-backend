from graphene_django import DjangoObjectType
from .models import (BaseUser, Member, Association, AssociationGroup,
                     AssociationGroupMember, AssociationType as
                     AssociationTypeModel, ExpectedAssociationMembersNumber)

import graphene

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from guardian.shortcuts import assign_perm, remove_perm


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


# mutations
class MemberAddMutation(graphene.Mutation):
    class Arguments:

        association = graphene.ID()

    success = graphene.Boolean()
    member = graphene.Field(MemberType)

    def mutate(root, info, association):
        association = Association.objects.get(id=association)

        member = Member.objects.create(association=association,
                                       user=info.context.user)
        success = True
        return MemberAddMutation(member=member, success=success)


class MemberAddByAdminMutation(graphene.Mutation):
    class Arguments:

        association = graphene.ID()
        user = graphene.String()

    success = graphene.Boolean()
    member = graphene.Field(MemberType)

    def mutate(root, info, association, user):

        association = Association.objects.get(id=association)
        user_ = BaseUser.objects.get(key=user)
        member = Member.objects.create(association=association, user=user_)
        success = True

        return MemberAddMutation(member=member, success=success)


class MemberDeleteMutation(graphene.Mutation):
    class Arguments:
        user = graphene.String()
        association = graphene.ID()

    success = graphene.Boolean()
    member = graphene.Field(MemberType)

    def mutate(root, info, association, user):

        member = Member.objects.filter(association__pk=association,
                                       user__key=user).delete()
        success = True
        return MemberDeleteMutation(member=member, success=success)


class MemberArchiveMutation(graphene.Mutation):
    class Arguments:
        user = graphene.String()
        association = graphene.ID()

    success = graphene.Boolean()
    member = graphene.Field(MemberType)

    def mutate(root, info, association, user):

        member = Member.objects.get(association__pk=association,
                                    user__key=user)
        member.is_archived = True
        member.save()
        success = True
        return MemberAddMutation(member=member, success=success)


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

    def mutate(root, info, id):
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

    def mutate(root, info, association, description):
        association = Association.objects.get(id=association)
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

    def mutate(root, info, name, association, group_type):
        association = Association.objects.get(id=association)
        _group = AssociationGroup.objects.create(name=name,
                                                 association=association,
                                                 group_type=group_type)
        success = True
        return AssociationGroupCreationMutation(group=_group, success=success)


class AssociationGroupDeleteMutation(graphene.Mutation):
    class Arguments:
        group = graphene.ID()
        association = graphene.ID()

    success = graphene.Boolean()
    group = graphene.Field(AssociationGroupType)

    def mutate(root, info, group, association):
        association = Association.objects.get(id=association)
        _group = AssociationGroup.objects.filter(id=group,
                                                 association=association)
        _group.delete()
        success = True
        return AssociationGroupCreationMutation(group=_group.first(),
                                                success=success)


class AssociationGroupMemberAddMutation(graphene.Mutation):
    class Arguments:
        member = graphene.ID()
        group = graphene.ID()

    success = graphene.Boolean()
    member = graphene.Field(AssociationGroupMemberType)

    def mutate(root, info, member, group):
        _member = Member.objects.get(id=member)
        _group = AssociationGroup.objects.get(id=group)
        member = AssociationGroupMember.objects.create(member=_member,
                                                       group=_group)
        success = True
        return AssociationGroupMemberAddMutation(member=member,
                                                 success=success)


class AssociationGroupMemberRemoveMutation(graphene.Mutation):
    class Arguments:
        member = graphene.ID()
        group = graphene.ID()

    success = graphene.Boolean()
    member = graphene.Field(AssociationGroupMemberType)

    def mutate(root, info, member, group):
        group_member = AssociationGroupMember.objects.filter(member=member,
                                                             group=group)
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

    def mutate(root, info, permission, association, member):
        _association = Association.objects.get(id=association)
        _member = Member.objects.get(id=member)
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

    def mutate(root, info, permission, association, member):
        _association = Association.objects.get(id=association)
        _member = Member.objects.get(id=member)
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

    def mutate(root, info, permission, association, group, member):
        _association = Association.objects.get(id=association)
        _group = AssociationGroup.objects.get(id=group,
                                              association__id=association)
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

    def mutate(root, info, permission, association, group, member):
        _association = Association.objects.get(id=association)
        _group = AssociationGroup.objects.get(id=group,
                                              association__id=association)
        _member = Member.objects.get(id=member)
        remove_perm(permission, _member.user, _group)
        success = True
        return OwnerRemoveGroupPermissionsToMembers(member=_member,
                                                    success=success)


# end mutations
class AccountsMutation(graphene.ObjectType):
    add_member = MemberAddMutation.Field()
    add_memeber_by_admin = MemberAddByAdminMutation.Field()
    delete_member = MemberDeleteMutation.Field()
    archive_member = MemberArchiveMutation.Field()

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
    get_all_association_object_permissions = graphene.List(
        ModelsPermissionType)
    get_all_association_group_object_permissions = graphene.List(
        ModelsPermissionType)
    get_all_association_member_object_permissions = graphene.List(
        ModelsPermissionType)
    get_all_association_group_member_object_permissions = graphene.List(
        ModelsPermissionType)

    def resolve_get_association_by_slug(root, info, slug):
        return Association.objects.get(slug=slug)

    def resolve_get_all_association_object_permissions(root, info):
        content_type = ContentType.objects.get_for_model(Association)
        return Permission.objects.filter(content_type=content_type)

    def resolve_get_all_association_group_object_permissions(root, info):
        content_type = ContentType.objects.get_for_model(AssociationGroup)
        return Permission.objects.filter(content_type=content_type)

    def resolve_get_all_association_member_object_permissions(root, info):
        content_type = ContentType.objects.get_for_model(Member)
        return Permission.objects.filter(content_type=content_type)

    def resolve_get_all_association_group_member_object_permissions(
            root, info):
        content_type = ContentType.objects.get_for_model(
            AssociationGroupMember)
        return Permission.objects.filter(content_type=content_type)
