from graphene_django import DjangoObjectType
from .models import (BaseUser, Member, Association, AssociationGroup,
                     AssociationGroupMember, AssociationType as AssociationTypeModel,
                     ExpectedAssociationMembersNumber)
import graphene


#types
class MemberType(DjangoObjectType):
    class Meta:
        model = Member
        fields = ['association', 'user', 'is_owner']


class AssociationType(DjangoObjectType):
    class Meta:
        model = Association
        fields = [
            'id','name', 'description', 'association_type',
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

        association_type = AssociationTypeModel.objects.get(id=association_type)

        association_min_max_numbers = ExpectedAssociationMembersNumber.objects.get(
            id=association_min_max_numbers)

        association = Association.objects.create(
            name=name,
            description=description,
            association_type=association_type,
            association_min_max_numbers=association_min_max_numbers)

        user = info.context.user
        user.is_association_owner = True
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
        return AssociationDeleteMutation(association=association_, success=success)


class AssociationUpdateDescriptionMutation(graphene.Mutation):
    class Arguments:
        association = graphene.ID()
        description = graphene.String()

    success = graphene.Boolean()
    association = graphene.Field(AssociationType)

    def mutate(root, info, association, description):
        association = Association.objects.filter(id=association)
        association.update(description=description)
        success = True
        return AssociationCreationMutation( association=association.first(),
                                           success=success)


class AssociationGroupCreationMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        association = graphene.ID()
        group_type = graphene.String()

    success = graphene.Boolean()
    group = graphene.Field(AssociationGroupType)

    def mutate(root, info, name, association, group_type):
        _group = AssociationGroup.objects.create(name=name,
                                                 association=association,
                                                 group_type=group_type)

        return AssociationGroupCreationMutation(group=_group, success=success)


class AssociationGroupDeleteMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        association = graphene.ID()

    success = graphene.Boolean()
    group = graphene.Field(AssociationGroupType)

    def mutate(root, info, name, association):
        _group = AssociationGroup.objects.delete(name=name,
                                                 association=association)

        return AssociationGroupCreationMutation(group=_group, success=success)


class AssociationGroupMemberAddMutation(graphene.Mutation):
    class Arguments:
        memeber = graphene.ID()
        group = graphene.ID()

    success = graphene.Boolean()
    member = graphene.Field(AssociationGroupMemberType)

    def mutate(root, info, member, group):
        member = AssociationGroupMember.objects.create(member__id=member,
                                                       group__id=group)
        success = True
        return AssociationGroupMemberAddMutation(member=member,
                                                 success=success)


# end mutations


class AccountsMutation(graphene.ObjectType):
    add_member = MemberAddMutation.Field()
    add_memeber_by_admin = MemberAddByAdminMutation.Field()
    delete_member = MemberDeleteMutation.Field()
    archive_member = MemberArchiveMutation.Field()

    create_association = AssociationCreationMutation.Field()
    update_association_description = AssociationUpdateDescriptionMutation.Field()
    delete_assciation = AssociationDeleteMutation.Field()

    create_group = AssociationGroupCreationMutation.Field()
    delete_group = AssociationGroupDeleteMutation.Field()

    add_members_group = AssociationGroupMemberAddMutation.Field()
