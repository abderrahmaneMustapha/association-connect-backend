import json

from django.test import TestCase
from graphene.test import Client

from backend.schema import schema
from .models import Association, AssociationType, ExpectedAssociationMembersNumber, BaseUser

from django.test import RequestFactory

class MyFancyTestCase(TestCase):
    databases = {"test_", "default"}
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

        cls.user = BaseUser.objects.create(
            first_name="toumi",
            last_name="abderrahmane",
            email="abderrahmanemustapa@mail.com",
            is_association_owner=False)

        cls.req = RequestFactory().get('/')
        cls.req.user = cls.user
    
    
    def test_add_member(self):
        client = Client(schema, context_value=self.req)

        query = "mutation { addMember(association: %s ){success,member{association{name}},}}"%(self.association.id)
        response = client.execute(query)
    
   
        assert  'errors' not in response 
    
    def test_add_member_by_admin(self): 
        client = Client(schema, context_value=self.req)   

        query = "mutation{addMemeberByAdmin(association:%s, user: \"%s\"){success}}" %(self.association.id, self.user.key)
        response = client.execute(query)

        assert  'errors' not in response
    
    def 