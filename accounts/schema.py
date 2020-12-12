from graphene_django import DjangoObjectType
from .models import BaseUser,Member, Association, AssociationGroup, AssociationGroupMember
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
            'name', 'description', 'association_type',
            'association_min_max_numbers'
        ]


class AssociationGroupType(DjangoObjectType):
    class Meta:
        model = AssociationGroup
        fields = ['name', 'association', 'group_type']

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
        member = Member.objects.create(association=association,
                                       user=user_)
        success = True

        return MemberAddMutation(member=member, success=success)
class MemberDeleteMutation(graphene.Mutation):
    class Arguments:
        user = graphene.String()
        association = graphene.ID()

    success = graphene.Boolean()
    member = graphene.Field(MemberType)

    def mutate(root, info, association, user ):      

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

        association = Association.objects.get(pk=association)

        member = Member.objects.get(association__id=association,
                                       user=user)
        member.is_archived = True
        member.save()
        success = True
        return MemberAddMutation(member=member, success=success)

class AssciationCreationMutation(graphene.Mutation):

    class Arguments:
        name = graphene.String()
        description = graphene.String()
        association_type = graphene.ID()
        association_min_max_numbers = graphene.ID()
        phone = graphene.String()
        email  =  graphene.String()

    success = graphene.Boolean()
    association = graphene.Field(AssociationType)

    def mutate(root, info, name, description, association_type,
               association_min_max_numbers, phone, email):

        association = Association.objects.create(
            name=name,
            description=description,
            association_type=association_type,
            association_min_max_numbers=association_min_max_numbers)

        user = info.context.user
        user.is_association_owner = True
        user.save()

        Member.objects.create(user=user, association=association,  is_owner=True)

        success = True

        return AssciationCreationMutation(association=association,
                                          success=success)

class AssciationDeleteMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
    
    success = graphene.Boolean()
    association = graphene.Field(AssociationType)

    def mutate(root, info, id):
        association = Association.objects.get(pk=id)
        success = True
        return AssciationDeleteMutation(association=association, success=success)
class AssociationUpdateDescriptionMutation(graphene.Mutation):
    class Arguments:
        description = graphene.String()

    success = graphene.Boolean()
    association = graphene.Field(AssociationType)

    def mutate(root, info, description):
        assciation = Association.objects.update(description=description)
        success = True
        return AssciationCreationMutation(assciation=assciation,
                                          success=success)
class AssociationGroupCreationMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        association = graphene.ID()
        group_type = graphene.String()
    success =  graphene.Boolean()
    group  = graphene.Field(AssociationGroupType)

    def mutate(root, info, name, association, group_type):
        _group = AssociationGroup.objects.create(name=name, association=association, group_type=group_type)

        return AssociationGroupCreationMutation(group=_group, success=success)

class AssociationGroupDeleteMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        association = graphene.ID()

    success =  graphene.Boolean()
    group  = graphene.Field(AssociationGroupType)

    def mutate(root, info, name, association):
        _group = AssociationGroup.objects.delete(name=name, association=association)

        return AssociationGroupCreationMutation(group=_group, success=success)
class AssociationGroupMemberAddMutation(graphene.Mutation):
    class Arguments:
        memeber = graphene.ID()
        group = graphene.ID()

    success = graphene.Boolean()
    member = graphene.Field(AssociationGroupMemberType)

    def mutate(root, info, member, group):
        member = AssociationGroupMember.objects.create(member__id=member, group__id=group)
        success = True
        return AssociationGroupMemberAddMutation(member=member, success=success)
# end mutations


class AccountsMutation(graphene.ObjectType):
    add_member =  MemberAddMutation.Field()
    add_memeber_by_admin = MemberAddByAdminMutation.Field()
    delete_member = MemberDeleteMutation.Field()
    archive_member = MemberArchiveMutation.Field()

    create_association = AssciationCreationMutation.Field()
    update_association_description = AssociationUpdateDescriptionMutation.Field()
    delete_assciation = AssciationDeleteMutation.Field()

    create_group = AssociationGroupCreationMutation.Field()
    delete_group = AssociationGroupDeleteMutation.Field()

    add_members_group = AssociationGroupMemberAddMutation.Field()

