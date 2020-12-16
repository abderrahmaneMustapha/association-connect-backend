from django.test import TestCase
from graphene.test import Client

from datetime import date,timedelta

from backend.schema import schema
from accounts.models import (Association, AssociationType,
                             ExpectedAssociationMembersNumber, AssociationMembership, Member)
from .models import (Form, Association, BaseUser, Member, Costs)


class MembershipMutationsTestCase(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls):
        cls.user = BaseUser.objects.create(
            first_name="toumi",
            last_name="abderrahmane",
            email="abderrahmanemustapa@mail.com",
            is_association_owner=False)

        cls.association_type = AssociationType.objects.create(
            name="sport", description="a sport activitys")

        cls.association_min_max_numbers = ExpectedAssociationMembersNumber.objects.create(
            max_number=30, min_number=2000)

        cls.association = Association.objects.create(
            name="dz algeria",
            description="we are dz algeria a perfect organizatoin",
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
        cls.cost  = Costs.objects.create(
            form = cls.form,
            description="a new cost of membership", 
            amount=11, 
            membership_time=timedelta(days =-1, seconds = 68400), 
            show_in_form=True
        )

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


    def test_add_membership_cost_mutation(self):
        client = Client(schema)

        query = """mutation{
            addCostToForm(form:%s, amount:%s, description:\"%s\", 
                membershipTime:\"%s\", showInForm:true){
                cost{id, description}
                success
            }
        }""" % (self.form.id, 234, "azazeazeazeaze",
                        timedelta(days =-1, seconds = 68400) )
        
        response = client.execute(query)
        assert 'errors' not in response 
    
    def test_add_membership_cost_payed_mutation(self):
        client = Client(schema)

        query = """mutation{
            addUserPayedCosts(cost:%s, user:\"%s\"){
                    cost{id, cost{id,description}}
            }
        }""" % (self.cost.id, self.user.key )
        
        response = client.execute(query)
        assert 'errors' not in response 

        member_exists = Member.objects.filter(user__key=self.user.key).exists()
        assert member_exists == True

        membership_exists = AssociationMembership.objects.filter(member__user__key=self.user.key).exists()
        assert  membership_exists

    

