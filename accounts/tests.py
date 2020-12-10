import json

from graphene_django.utils.testing import GraphQLTestCase
from graphene.test import Client

from backend.schema import schema
from .models import Association, AssociationType, ExpectedAssociationMembersNumber, BaseUser

from django.test import RequestFactory

class MyFancyTestCase(GraphQLTestCase):

    
    association_type = AssociationType.objects.create(
        name="sport", description="a sport activitys")

    association_min_max_numbers = ExpectedAssociationMembersNumber.objects.create(
        max_number=30, min_number=2000)

    association = Association.objects.create(
        name="dz algeria",
        description="we are dz algeria a perefect organizatoin",
        association_min_max_numbers=association_min_max_numbers,
        association_type=association_type)

    user = BaseUser.objects.create_user(
        first_name="toumi",
        last_name="abderrahmane",
        email="abderrahmanemustapha@mail.com",
        password="azeaz223éé",
        is_association_owner=False)

    req = RequestFactory().get('/')
    req.user = user

    def test_add_memeber(self):
       
        client = Client(schema, context_value=self.req)

        query = "mutation { addMember(association: %s ){success,member{association{name}},}}"%(self.association.id)
        response = client.execute(query)
    
       
        assert  'errors' not in response 
