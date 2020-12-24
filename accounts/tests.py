from django.test import TestCase
from graphene.test import Client

from backend.schema import schema
from .models import (Association, AssociationType,
                     ExpectedAssociationMembersNumber, BaseUser, Member,
                     AssociationGroup, AssociationGroupMember, AssociationGroupMember)

from django.test import RequestFactory


class AccountsMutationsTestCase(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls):

        cls.association_type = AssociationType.objects.create(
            name="sport", description="a sport activitys")

        cls.association_min_max_numbers = ExpectedAssociationMembersNumber.objects.create(
            max_number=30, min_number=2000)

        cls.association = Association.objects.create(
            name="dz algeria",
            description="we are dz algeria a perefect organizatoin",
            association_min_max_numbers=cls.association_min_max_numbers,
            association_type=cls.association_type)

        cls.group = AssociationGroup.objects.create(name="Leader",
                                                   association=cls.association,
                                                   group_type="S")

        cls.user = BaseUser.objects.create(
            first_name="toumi",
            last_name="abderrahmane",
            email="abderrahmanemustapa@mail.com",
            is_association_owner=False)

        cls.delete_user = BaseUser.objects.create(
            first_name="toumidelete_",
            last_name="abderrahmanedelete_",
            email="abderrahmanemustapadelete_@mail.com",
            is_association_owner=False)

        cls.delete_member = Member.objects.create(user=cls.delete_user,
                                                  association=cls.association)

        cls.archive_user = BaseUser.objects.create(
            first_name="toumiarchive_",
            last_name="abderrahmanearchive_",
            email="abderrahmanemustapaarchive_@mail.com",
            is_association_owner=False)

        cls.archive_member = Member.objects.create(user=cls.archive_user,
                                                   association=cls.association)

        cls.req = RequestFactory().get('/')
        cls.req.user = cls.user

    def test_add_member(self):
        client = Client(schema, context_value=self.req)

        query = "mutation { addMember(association: %s ){success,member{association{name}},}}" % (
            self.association.id)
        response = client.execute(query)

        assert 'errors' not in response

    def test_add_member_by_admin(self):
        client = Client(schema, context_value=self.req)

        query = "mutation{addMemeberByAdmin(association:%s, user: \"%s\"){success}}" % (
            self.association.id, self.user.key)
        response = client.execute(query)

        assert 'errors' not in response

    def test_delete_member(self):
        client = Client(schema, context_value=self.req)

        query = "mutation{deleteMember(association:%s , user:\"%s\"){success}}" % (
            self.association.id, self.delete_user.key)
        response = client.execute(query)

        member_deleted = Member.objects.filter(
            user=self.delete_user, association=self.association).exists()

        assert 'errors' not in response
        assert member_deleted == False

    def test_archive_member(self):
        client = Client(schema, context_value=self.req)

        query = "mutation{archiveMember(association: %s , user:\"%s\"){success}}" % (
            self.association.id, self.archive_user.key)
        response = client.execute(query)

        member_archived = Member.objects.get(user=self.archive_user,
                                             association=self.association)

        assert 'errors' not in response
        assert member_archived.is_archived == True

    def test_create_association(self):
        client = Client(schema, context_value=self.req)

        query = """mutation {createAssociation(associationMinMaxNumbers: %s , associationType:  %s , 
  				description:"dqsd", email: "newass@mail.com"
  				, name: "new asso", phone: "+213780195168")
                    {
                            success,association{id,name}
                    }
                }""" % (self.association_min_max_numbers.id,
                        self.association_type.id)

        response = client.execute(query)
        assert 'errors' not in response

        member_exists = Member.objects.filter(user=self.user).exists()
        assert member_exists == True

        member = Member.objects.get(user=self.user)
        assert member.is_owner

        assert member.user.is_association_owner

    def test_create_association_no_register(self):
        client = Client(schema, context_value=self.req)

        query = """mutation {createAssociationNoRegister( associationType:  %s , 
  				, name: "new asso", email:"aaa@mail.com" ,phone: "+213780195168")
                    {
                            success,association{id,name}
                    }
                }""" % (self.association_type.id)

        response = client.execute(query)
        print(response)
        assert 'errors' not in response

        member_exists = Member.objects.filter(user=self.user).exists()
        assert member_exists == True

        member = Member.objects.get(user=self.user)
        assert member.is_owner

        assert member.user.is_association_owner

    def test_delete_association(self):
        client = Client(schema, context_value=self.req)

        query = """
            mutation {
                deleteAssciation(id:%s){
                    success,
                    association{id,name,description}
                }
            }
        """ % (self.association.id)

        response = client.execute(query)
        assert 'errors' not in response

        association_exists = Association.objects.filter(
            id=self.association.id).exists()
        assert association_exists == False

    def test_update_association_description(self):
        client = Client(schema, context_value=self.req)
        new_association_description = "new updated description"
        query = """
        mutation {
            updateAssociationDescription(association: %s , description: \"%s\") {
                success
                association {
                    id
                    name
                    description
                }
            }
        }
        """ % (self.association.id, new_association_description)

        response = client.execute(query)
        assert 'errors' not in response

        association_description = Association.objects.get(
            id=self.association.id).description
        assert new_association_description == association_description

    def test_association_group_creation(self):
        client = Client(schema, context_value=self.req)

        query = """
            mutation {
                createGroup(association:%s, groupType:"S", name:\"%s\"){
                    success,
                    group{id, name, association{id}, groupType}
                }
            }

        """ % (self.association.id, "Amateur")

        response = client.execute(query)
        assert 'errors' not in response

        query = """
            mutation {
                createGroup(association:%s, groupType:"D", name:\"%s\"){
                    success,
                    group{id, name, association{id}, groupType}
                }
            }

        """ % (self.association.id, "Seniors")

        response = client.execute(query)
        assert 'errors' not in response

    def test_association_group_delete(self):
        client = Client(schema, context_value=self.req)

        query = """
            mutation {
                deleteGroup(association:%s, group:%s){
                    success,
                    group{id, name,association{id}}
                }
            }
        """ %(self.association.id, self.group.id)

        response = client.execute(query)
        assert 'errors' not in response

        group_exist  = AssociationGroup.objects.filter(id=self.group.id).exists()
        assert  group_exist == False
    
    def test_association_add_member_group(self):
        client = Client(schema, context_value=self.req)

        query="""
        mutation {
            addMemberGroup(member:%s, group:%s){
                success
                member{member{id}}
            }
        }
        """%(self.delete_member.id, self.group.id)
        
        response = client.execute(query)
        assert 'errors' not in response

        group_exists = AssociationGroupMember.objects.filter(member=self.delete_member.id, id=self.group.id).exists()
        assert group_exists == True

    def test_association_remove_member_group(self):
        client = Client(schema, context_value=self.req)

        query="""
            mutation {
                removeMemberGroup(member:%s, group:%s){
                    success
                    member{member{id}}
                }
            }
        """%(self.delete_member.id, self.group.id)
        
        response = client.execute(query)
      
        assert 'errors' not in response

        group_exists = AssociationGroupMember.objects.filter(member=self.delete_member.id, id=self.group.id).exists()
        assert group_exists == False

    def test_give_member_association_permission(self):
        client = Client(schema, context_value=self.req)
        permission = "update_association_info"

        query =  """
            mutation{
                giveMemberAssociationPermission(association:%s, member:%s, permission:\"%s\"){
                    success,
                    member{id, association{id}, isOwner}
                }
            }
        """ %(self.association.id, self.delete_member.id, permission )
        response = client.execute(query)
        assert 'errors' not in response

        user = Member.objects.get(id=self.delete_member.id).user
        association = Association.objects.get(id=self.association.id)

        assert user.has_perm(permission, association) == True

    def test_give_member_association_permission(self):
        client = Client(schema, context_value=self.req)
        permission = "update_association_info"

        query =  """
            mutation{
                removeMemberAssociationPermission(association:%s, member:%s, permission:\"%s\"){
                    success,
                    member{id, association{id}, isOwner}
                }
            }
        """ %(self.association.id, self.delete_member.id, permission )
        response = client.execute(query)
        assert 'errors' not in response

        user = Member.objects.get(id=self.delete_member.id).user
        association = Association.objects.get(id=self.association.id)

        assert user.has_perm(permission, association) == False

    def test_give_member_association_permission(self):
        client = Client(schema, context_value=self.req)
        permission = "view_group_member_info"

        query =  """
            mutation{
                giveMemberGroupPermission(association:%s, member:%s, group:%s, permission:\"%s\"){
                    success,
                    member{id, association{id}, isOwner}
                }
            }
        """ %(self.association.id, self.delete_member.id, self.group.id, permission )
        response = client.execute(query)
        assert 'errors' not in response

        user = Member.objects.get(id=self.delete_member.id).user
        group = AssociationGroup.objects.get(id=self.group.id)

        assert user.has_perm(permission, group) == True

    def test_give_member_association_permission(self):
        client = Client(schema, context_value=self.req)
        permission = "view_group_member_info"

        query =  """
            mutation{
                removeMemberGroupPermission(association:%s, member:%s, group:%s, permission:\"%s\"){
                    success,
                    member{id, association{id}, isOwner}
                }
            }
        """ %(self.association.id, self.delete_member.id, self.group.id, permission )
        response = client.execute(query)
        assert 'errors' not in response

        user = Member.objects.get(id=self.delete_member.id).user
        group = AssociationGroup.objects.get(id=self.group.id)

        assert user.has_perm(permission, group) == False
