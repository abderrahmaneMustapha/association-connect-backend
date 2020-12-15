from django.test import TestCase
from graphene.test import Client

from datetime import date

from backend.schema import schema
from accounts.models import (Association, AssociationType,
                             ExpectedAssociationMembersNumber)
from .models import (Form, Association, BaseUser, Member)


class MembershipMutationsTestCase(TestCase):
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

        cls.form = Form.objects.create(
            association=cls.association,
            title="Add new members",
            description=
            "we can add new member to this  form by filling the fields here",
            email="assoform@mail.com",
            start_date=date.fromisoformat('2020-12-24'),
            days=44)

    def test_add_form_meta_data(self):
        client = Client(schema)

        query = """mutation{
                    addFormMeta(association:%s, 
                    days:%s, 
                    description:\"%s\", 
                    email:\"%s\", 
                    startDate:\"%s\", 
                    title:\"%s\")
                    {
                    
                    form{id,title},
                    success
                    }
                }""" % (self.association.id, 55, "azazeazeazeaze",
                        "abdou@mail.com", date.today(), "New form")

        response = client.execute(query)

        assert 'errors' not in response


        query = """mutation{
                    addFormMeta(association:%s, 
                    days:%s, 
                    description:\"%s\", 
                    email:\"%s\", 
                    startDate:\"%s\", 
                    title:\"%s\")
                    {
                    
                    form{id,title, email},
                    success
                    }
                }""" % (self.association.id, 55, "azazeazeazeaze",
                        "abdoumail", date.today(), "New form")

        response = client.execute(query)
        assert "{'email': ['Enter a valid email address.']}"  in response['errors'][0]['message']