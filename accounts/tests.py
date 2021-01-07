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
        
        cls.association1 = Association.objects.create(
            name="dz el kheir",
            slug="dz-el-kheir",
            description="organization description 1",
            association_min_max_numbers=cls.association_min_max_numbers,
            association_type=cls.association_type)

        cls.group = AssociationGroup.objects.create(name="Leader",
                                                   association=cls.association,
                                                   group_type="S")

        cls.group1 = AssociationGroup.objects.create(name="Novices",
                                                   association=cls.association1,
                                                   group_type="S")
        
        cls.group2 = AssociationGroup.objects.create(name="Minecraft players",
                                                   association=cls.association1,
                                                   group_type="S")
        
        cls.group3 = AssociationGroup.objects.create(name="Dota players",
                                                   association=cls.association1,
                                                   group_type="D")

        cls.group3 = AssociationGroup.objects.create(name="LOL players",
                                                   association=cls.association1,
                                                   group_type="D")

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
        
        cls.another_member = Member.objects.create(user=cls.user, association=cls.association1)

        cls.archive_user = BaseUser.objects.create(
            first_name="toumiarchive_",
            last_name="abderrahmanearchive_",
            email="abderrahmanemustapaarchive_@mail.com",
            is_association_owner=False)

        cls.archive_member = Member.objects.create(user=cls.archive_user,
                                                   association=cls.association)

        cls.req = RequestFactory().get('/')
        cls.req.user = cls.user


    # mutations tests
    def test_add_member_by_admin(self):
        client = Client(schema, context_value=self.req)

        Member.objects.create( association= self.association, user=self.user)
        query = "mutation{addMemeberByAdmin(association:%s, user: \"%s\"){success}}" % (
            self.association.id, self.user.key)
        response = client.execute(query)

        assert 'errors' not in response

    def test_delete_member(self):
        client = Client(schema, context_value=self.req)
        Member.objects.create(user=self.user,association=self.association, is_owner=True)
        query = "mutation{deleteMember(association:%s , user:\"%s\"){success}}" % (
            self.association.id, self.delete_user.key)
        response = client.execute(query)

        member_deleted = not Member.objects.filter(
            user=self.delete_user, association=self.association).exists()
        assert 'errors' not in response
        assert member_deleted == True

    def test_archive_member(self):
        client = Client(schema, context_value=self.req)
        Member.objects.create(user=self.user,association=self.association, is_owner=True)
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
        
        association_id = response['data']['createAssociation']['association']['id']
        member = Member.objects.filter(user=self.user, association__id=association_id).last()
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
    
        assert 'errors' not in response

        member_exists = Member.objects.filter(user=self.user).exists()
        assert member_exists == True
       
        association_id = response['data']['createAssociationNoRegister']['association']['id']
        member = Member.objects.get(user=self.user, association__id=association_id)        
        assert member.is_owner

        assert member.user.is_association_owner

    def test_delete_association(self):
        client = Client(schema, context_value=self.req)
        Member.objects.create(user=self.user, association=self.association, is_owner=True)
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
        Member.objects.create(user=self.user, association=self.association, is_owner=True)

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
        Member.objects.create(user=self.user, association=self.association, is_owner=True)
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

        group_exists = AssociationGroup.objects.filter(association=self.association.id, name="Amateur").exists()
        assert group_exists == True

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

        group_exists = AssociationGroup.objects.filter(association=self.association.id, name="Seniors").exists()
        assert group_exists == True

    def test_association_group_delete(self):
        client = Client(schema, context_value=self.req)
        Member.objects.create(user=self.user, association=self.association, is_owner=True)
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
        Member.objects.create(user=self.user, association=self.association, is_owner=True)
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
        Member.objects.create(user=self.user, association=self.association, is_owner=True)
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
        Member.objects.create(user=self.user, association=self.association, is_owner=True)
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
    
    
    def test_remove_member_association_permission(self):
        client = Client(schema, context_value=self.req)
        Member.objects.create(user=self.user, association=self.association, is_owner=True)
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

    # queries tests
    def test_get_association_by_slug(self):
        client = Client(schema, context_value=self.req)

        query = """ 
            query{
                getAssociationBySlug(slug:\"%s\"){
                    id,
                    slug,
                    name, 
                    description,
                }
            }
        """ %(self.association1.slug)

        response = client.execute(query)
        assert 'errors' not in response

    def test_get_all_associations(self):
        client = Client(schema, context_value=self.req)
        query = """
            query{
                getAllAssociations{
                    id,
                }
            }
        """

        response = client.execute(query)
        assert 'errors' not in response

        assert [{'id': '1'}, {'id': '2'}] == response['data']['getAllAssociations']

    def test_get_all_associations_statique_groups(self):

        client = Client(schema, context_value=self.req)
        Member.objects.filter(user=self.user, association=self.association1).update(is_owner=True)
        query = """
            query{
                getAllAssociationsStatiqueGroups(slug:\"%s\"){
                    id,
                    name,
                    association{id,name},
                    groupType
                }
            }
        """ %(self.association1.slug)

        response = client.execute(query)
        assert 'errors' not in response

        groups =  response['data']['getAllAssociationsStatiqueGroups']
        assert groups is not None

        for group in groups:
            assert group['groupType'] == "S"
    
    def test_get_all_associations_dynamique_groups(self):
        client = Client(schema, context_value=self.req)
        Member.objects.filter(user=self.user, association=self.association1).update(is_owner=True)
        query = """
            query{
                getAllAssociationsDynamiqueGroups(slug:\"%s\"){
                    id,
                    name,
                    association{id,name},
                    groupType
                }
            }
        """ %(self.association1.slug)

        response = client.execute(query)
        assert 'errors' not in response

        groups =  response['data']['getAllAssociationsDynamiqueGroups']
        assert groups is not None

        for group in groups:
            assert group['groupType'] == "D"

    def test_get_associations_group_by_id(self):
        client = Client(schema, context_value=self.req)
         
        Member.objects.filter(user=self.user, association=self.association1).update(is_owner=True)
        query = """
            query{
                getAssociationsGroupById(id:%s){
                    id,
                    name,
                    association{id,name},
                    groupType
                }
            }
        """ %(self.group1.id)

        response = client.execute(query)
        assert 'errors' not in response
        

    def test_get_associations_members(self):
        client = Client(schema, context_value=self.req)
         
        Member.objects.filter(user=self.user, association=self.association1).update(is_owner=True)
        Member.objects.filter(user=self.delete_user, association=self.association1).update(is_owner=True)
     
        query = """
            query{
                getAssociationsMembers(slug:\"%s\"){
                    id,
                    user{key, email}
                }
            }
        """ %(self.association1.slug)

        response = client.execute(query)

        assert 'errors' not in response

    def test_get_association_member_by_id(self):
        client = Client(schema, context_value=self.req)
         
        Member.objects.filter(user=self.user, association=self.association1).update(is_owner=True)
        member = Member.objects.create(user=self.delete_user, association=self.association1)
     
        query = """
            query{
                getAssociationMemberById(id:%s){
                    id,
                    user{key, email}
                }
            }
        """ %(member.id)

        response = client.execute(query)
        assert 'errors' not in response
        data = response['data']['getAssociationMemberById']

        assert data is not None

  