from django.test import TestCase
from graphene.test import Client

from datetime import date, timedelta
import textwrap

from backend.schema import schema
from accounts.models import (Association, AssociationType,
                             ExpectedAssociationMembersNumber,
                             AssociationMembership, Member, AssociationGroupMember)
from .models import (Form, Association, BaseUser, Member, Costs, FieldType,
                     Field, FieldData, UserPayedCosts, JoinRequest, AssociationGroupJoinRequest, AssociationGroup)
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory


class MembershipMutationsTestCase(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls):

        cls.user = BaseUser.objects.create(
            first_name="toumi",
            last_name="abderrahmane",
            email="abderrahmanemustapa@mail.com",
            is_association_owner=False)

        
        cls.user1 = BaseUser.objects.create(
            first_name="haboboa",
            last_name="najik",
            email="kajajj@mail.com",
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

        cls.group1 = AssociationGroup.objects.create(
            name = "group1",
            association = cls.association,
            group_type = "D"
        )

        cls.group2 = AssociationGroup.objects.create(
            name = "group2",
            association = cls.association,
            group_type = "D"
        )
        cls.association_add_to_request = Association.objects.create(
            name="dz algeria 1",
            description="here we are new org",
            association_min_max_numbers=cls.association_min_max_numbers,
            association_type=cls.association_type)

        cls.association.slugify_()
        cls.association.save()

        cls.form = Form.objects.create(
            association=cls.association,
            title="Add new members",
            description=
            "we can add new member to this  form by filling the fields here",
            email="assoform@mail.com",
            start_date=date.fromisoformat('2020-12-24'),
            days=44)

        cls.form_add_to_request = Form.objects.create(
            association=cls.association_add_to_request,
            title="Add new members",
            description=
            "we can add new member to this  form by filling the fields here",
            email="assoform@mail.com",
            start_date=date.fromisoformat('2020-12-24'),
            days=44,
            add_to_request=True)

        cls.form_second = Form.objects.create(
            association=cls.association,
            title="Add new members second",
            description=
            "we can add new member to this  form by filling the fields here",
            email="assoform@mail.com",
            start_date=date.fromisoformat('2020-12-24'),
            days=44)

        cls.cost = Costs.objects.create(form=cls.form,
                                        description="a new cost of membership",
                                        amount=11,
                                        membership_time=2,
                                        show_in_form=True)

        cls.cost_form_to_request = Costs.objects.create(
            form=cls.form_add_to_request,
            description="a new cost of membership",
            amount=991,
            membership_time=2,
            show_in_form=True)

        cls.user_payed_cost = UserPayedCosts.objects.create(user=cls.user,
                                                            cost=cls.cost)

        cls.user_payed_cost_to_request = UserPayedCosts.objects.create(
            user=cls.user, cost=cls.cost_form_to_request)

        cls.field_type = FieldType.objects.create(name="char")

        cls.field = Field.objects.create(form=cls.form_second,
                                         label="azeaze",
                                         description="azeaze",
                                         placeholder="qazeaze",
                                         show_in_form=True,
                                         required=True,
                                         type=cls.field_type)

        cls.field_second = Field.objects.create(
            form=cls.form,
            label="new label",
            description=" new label azeaze",
            placeholder=" new label qazeaze",
            show_in_form=True,
            required=True,
            type=cls.field_type)

        cls.field_data = FieldData.objects.create(
            field=cls.field_second,
            user=cls.user,
            data={"name": "abderrahmane"})

        cls.req = RequestFactory().get('/')
        cls.req.user = cls.user

    def test_add_form_meta_data(self):
        client = Client(schema, context_value=self.req)
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b')
        image = SimpleUploadedFile(name='test_image.jpg',
                                   content=small_gif,
                                   content_type='image/jpeg')

        query = textwrap.dedent('''mutation{{
                    addFormMeta(association:{0}, 
                    days:{1}, 
                    description:\"{2}\", 
                    email:\"{3}\", 
                    startDate:\"{4}\", 
                    title:\"{5}\"
                    link:"https://dzstartup.com",
                    phone:\"{6}\"
                    )
                    {{
                    
                    form{{id,title}},
                    success
                    }}
                }}''').strip("\n").format(self.association.id, 55,
                                          "azazeazeazeaze", "abdou@mail.com",
                                          date.today(), "New form",
                                          "+213780195168")

        response = client.execute(query)

        assert 'errors' not in response

        form_exist = Form.objects.filter(association=self.association,
                                         title="New form").exists()
        assert form_exist == True

        query = """mutation{
                    addFormMeta(association:%s, 
                    days:%s, 
                    description:\"%s\", 
                    email:\"%s\", 
                    startDate:\"%s\", 
                    title:\"%s\",
                    link:"https://dzstartup.com",
                    phone:\"%s\"
                    )
                    {
                    
                    form{id,title, email},
                    success
                    }
                }""" % (
            self.association.id,
            55,
            "azazeazeazeaze",
            "abdoumail",
            date.today(),
            "New form",
            "+213780195168",
        )

        response = client.execute(query)
        assert "{'email': ['Enter a valid email address.']}" in response[
            'errors'][0]['message']

    # mutations
    def test_add_membership_cost_mutation(self):
        client = Client(schema, context_value=self.req)
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)
        query = """mutation{
            addCostToForm(inputs : {associationSlug:\"%s\", title:\"%s\", amount:%s, description:\"%s\", 
                membershipTime:\"%s\", showInForm:true}){
                cost{id, description}
                success
            }
        }""" % (self.form.association.slug, "Free plan", 234, "azazeazeazeaze", 4)

        response = client.execute(query)
        assert 'errors' not in response
        cost = Costs.objects.filter(description="azazeazeazeaze",
                                           form=self.form)
        cost_exists = cost.exists()
        assert cost_exists == True

        assert cost.first().title == "Free plan"

    def test_add_membership_costs_mutation(self):
        client = Client(schema, context_value=self.req)
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)
        query = """mutation{
            addCostsToForm(inputs : [{associationSlug:\"%s\", title:\"%s\", amount:%s, description:\"%s\", 
                membershipTime:\"%s\", showInForm:true}, {associationSlug:\"%s\", title:\"%s\", amount:%s, description:\"%s\", 
                membershipTime:\"%s\", showInForm:true}]){
                cost{id, description}
                success
            }
        }""" % (self.form.association.slug, "Pro plan", 234, "azazeazeazeaze", 6,
                self.form.association.slug, "Mythic plan", 264, "azeazeazeaze", 8)

        response = client.execute(query)
        assert 'errors' not in response

        cost_count = Costs.objects.filter(form=self.form).count()
        assert cost_count == 2

    def test_add_membership_cost_payed_mutation(self):
        client = Client(schema)

        query = """mutation{
            addUserPayedCosts(cost:%s, user:\"%s\"){
                    cost{id, cost{id,description}}
            }
        }""" % (self.cost.id, self.user1.key)

        response = client.execute(query)
        assert 'errors' not in response

    def test_add_multi_membership_cost_payed_mutation_faile(self):
        client = Client(schema)
        query = """mutation{
            addUserPayedCosts(cost:%s, user:\"%s\"){
                    cost{id, cost{id,description}}
            }
        }""" % (self.cost.id, self.user.key)

        response = client.execute(query)
        assert 'errors'  in response

    def test_add_field_to_form_mutation(self):
        client = Client(schema, context_value=self.req)
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)

        description = "this is my field description"
        label = "field"
        placeholder = "please add field"
        query = """mutation{
            addFieldToForm(inputs : {description:\"%s\", associationSlug:\"%s\", label:\"%s\", placeholder:\"%s\", 
            required:true, showInForm:true, type:\"%s\"}){
                field{id, label},
                success
            }
        }""" % (description, self.form.association.slug, label, placeholder,
                self.field_type.name)

        response = client.execute(query)

        assert 'errors' not in response

        existing_fields = Field.objects.filter(form=self.form).exists()
        assert existing_fields == True

        count_fields = Field.objects.filter(form=self.form).count()
        assert count_fields == 1

        name_field = Field.objects.filter(form=self.form).first().name 
        assert name_field == label

    def test_add_fields_to_form_mutation(self):
        client = Client(schema, context_value=self.req)
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)

        description = "this is my field description"
        label = "field"
        placeholder = "please add field"
        query = """mutation{
            addFieldsToForm(inputs: [
                {description:\"%s\", associationSlug:\"%s\", label:\"%s\", placeholder:\"%s\", 
                required:true, showInForm:true, type:\"%s\"}, 

                {description:\"%s\", associationSlug:\"%s\", label:\"%s\", placeholder:\"%s\", 
                required:true, showInForm:true, type:\"%s\"}
            ]){
                fields{id, label},
                success
            }
        }""" % (description, self.form.association.slug, label, placeholder,
                self.field_type.name, description, self.form.association.slug,
                label, placeholder, self.field_type.name)

        response = client.execute(query)
        assert 'errors' not in response

        exisiting_fields = Field.objects.filter(form=self.form).exists()
        assert exisiting_fields == True

        count_fields = Field.objects.filter(form=self.form).count()
        assert count_fields == 2

    def test_add_field_data_to_form_mutation(self):
        client = Client(schema, context_value=self.req)
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)

        data = {"name": "this is my field description"}

        query = """mutation{
            addDataToField(data:\"%s\", field:%s, user:\"%s\"){
                data{id, field{id, description}},
                success
            }
        }""" % (data, self.field.id, self.user.key)

        response = client.execute(query)

        assert 'errors' not in response

    def test_form_filled_by_user(self):

        client = Client(schema, context_value=self.req)

        query = """mutation{
            formFilled(userPayedCost:%s, groups:%s){
                success
            }
        }""" % (self.user_payed_cost.id,  [self.group1.id, self.group2.id])

        response = client.execute(query)
        assert 'errors' not in response

        member_exists = Member.objects.filter(
            user__key=self.user_payed_cost.user.key).exists()
        assert member_exists == True

        membership_exists = AssociationMembership.objects.filter(
            member__user__key=self.user_payed_cost.user.key).exists()
        assert membership_exists

        group_member1_count = AssociationGroupMember.objects.filter(group=self.group1, member__user=self.user_payed_cost.user).count()
        assert group_member1_count == 1

        group_member2_count = AssociationGroupMember.objects.filter(group=self.group2, member__user=self.user_payed_cost.user).count()
        assert group_member2_count == 1


        group_join_requests_exist = AssociationGroupJoinRequest.objects.filter(user_payed_cost=self.user_payed_cost_to_request).exists()
        
        assert  group_join_requests_exist == False

    def test_form_filled_by_user_to_join_request(self):
        client = Client(schema, context_value=self.req)
        Member.objects.create(user=self.user,
                              association=self.association_add_to_request,
                              is_owner=True)
        query = """mutation{
            formFilled(userPayedCost:%s, groups:%s){
                success
            }
        }""" % (self.user_payed_cost_to_request.id, [self.group1.id, self.group2.id])

        response = client.execute(query)
        assert 'errors' not in response

        joi_req = JoinRequest.objects.filter(
            user_payed_cost=self.user_payed_cost_to_request)

        join_exists = joi_req.exists()
        assert join_exists == True

        group_join_requests = AssociationGroupJoinRequest.objects.filter(user_payed_cost=self.user_payed_cost_to_request)

        group_join_requests_exist = group_join_requests.exists()
        assert group_join_requests_exist == True

        group_join_requests_count = group_join_requests.count()
        assert group_join_requests_count == 2

        join_request = joi_req.first()

        query = """mutation{
            acceptJoinRequest(joinRequest:%s){
                success,
            }
        }""" % (join_request.id)

        response = client.execute(query)
        assert 'errors' not in response
        
        accepted_join_req = JoinRequest.objects.get(
            user_payed_cost=self.user_payed_cost_to_request).accept
        assert accepted_join_req == True

        member = Member.objects.filter(user= self.user,  association=self.association_add_to_request, is_owner=False)
        assert member.exists() == True

        group_member1_count = AssociationGroupMember.objects.filter(group=self.group1, member__user=self.user_payed_cost.user).count()
        assert group_member1_count == 1

        group_member2_count = AssociationGroupMember.objects.filter(group=self.group2, member__user=self.user_payed_cost.user).count()
        assert group_member2_count == 1

     

        
        query = """mutation{
            declineJoinRequest(joinRequestId:%s){
                success,
            }
        }""" % (join_request.id)

        response = client.execute(query)
      
        assert 'errors' not in response

        accepted_join_req_exists  = JoinRequest.objects.filter(user_payed_cost=self.user_payed_cost_to_request).exists()
        assert accepted_join_req_exists == False

    # query
    def test_get_form_meta(self):
        client = Client(schema, context_value=self.req) 
        
        query = """
           query{
                getFormMeta(id:%s){
                    id
                    title
                    description
                    email
                }
            } 
        """ %(self.form.id)

        response = client.execute(query)
        assert 'errors' not in response

        data = response['data']['getFormMeta']
        assert data is not None 

    def test_get_form_by_association_slug(self):
        client = Client(schema, context_value=self.req) 
        self.association.slug = "asso-conn"
        self.association.save()
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)
        query = """
           query{
                getFormByAssociationSlug(slug:\"%s\"){
                    id
                    title
                    description
                    email
                }
            } 
        """ %(self.association.slug)

        response = client.execute(query)
        assert 'errors' not in response

        data = response['data']['getFormByAssociationSlug']
        assert data is not None

    def test_get_form_showed_fields(self):

        client = Client(schema, context_value=self.req) 
        self.association.slug = "aa-aa"
        self.association.save()
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)
        query = """
           query {
                getFormShowedFields(slug:\"%s\"){
                    id
                    label
                    description
                    placeholder
                }
            }
        """ %(self.association.slug)

        response = client.execute(query)
        assert 'errors' not in response

        data = response['data']['getFormShowedFields']
        assert data is not None

    def test_get_form_all_fields(self):

        client = Client(schema, context_value=self.req) 
        self.association.slug = "aa-aa"
        self.association.save()
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)
        query = """
           query {
                getFormAllFields(slug:\"%s\"){
                    id
                    label
                    description
                    placeholder
                }
            }
        """ %(self.association.slug)

        response = client.execute(query)
        assert 'errors' not in response

        data = response['data']['getFormAllFields']
        assert data is not None

    def test_get_form_showed_fields_data(self):
        
        client = Client(schema, context_value=self.req) 
     
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)
        query = """
           query {
                getFormShowedFieldsData(formId:\"%s\"){
                    id
                    field{id, label}
                }
            }
        """ %(self.form.id)

        response = client.execute(query)
        assert 'errors' not in response

        data = response['data']['getFormShowedFieldsData']
        assert data is not None 

    def test_get_form_all_fields_data(self):
        client = Client(schema, context_value=self.req) 
     
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)
        query = """
           query {
                getFormAllFieldsData(formId:\"%s\"){
                    id
                    field{id, label}
                }
            }
        """ %(self.form.id)

        response = client.execute(query)
        assert 'errors' not in response

        data = response['data']['getFormAllFieldsData']
        assert data is not None 
    
    def test_get_form_all_fields_user_data(self):
        client = Client(schema, context_value=self.req) 
     
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)

        
        query = """
           query {
                getFormAllFieldsUserData(formId:\"%s\", key:\"%s\"){
                    id
                    field{id, label}
                }
            }
        """ %(self.form.id, self.user.key)

        response = client.execute(query)
        assert 'errors' not in response

        data = response['data']['getFormAllFieldsUserData']
        assert data is not None 
    
    def test_get_form_all_costs(self):
        client = Client(schema, context_value=self.req) 
        self.association.slug = "aa-aa"
        self.association.save()
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)

        
        query = """
           query {
                getFormAllCosts(slug:\"%s\"){
                    id
                }
            }
        """ %(self.association.slug)

        response = client.execute(query)
        assert 'errors' not in response

        data = response['data']['getFormAllCosts']
        assert data is not None 
    
    
    def test_get_form_showed_costs(self):
        client = Client(schema, context_value=self.req) 
     
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)

        
        query = """
           query {
                getFormShowedCosts(slug:\"%s\"){
                    id
                }
            }
        """ %(self.association.slug)

        response = client.execute(query)
        assert 'errors' not in response

        data = response['data']['getFormShowedCosts']
        assert data is not None 
    
    def test_get_user_association_payed_costs(self):
        client = Client(schema, context_value=self.req) 
        self.association.slug = "aa-aa"
        self.association.save()
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)

        
        query = """
           query {
                getUserAssociationPayedCosts(slug:\"%s\"){
                    id
                }
            }
        """ %(self.association.slug)

        response = client.execute(query)
        assert 'errors' not in response

        data = response['data']['getUserAssociationPayedCosts']
        assert data is not None 
    
    def test_get_form_field_type(self):
        
        client = Client(schema, context_value=self.req) 
        query = """
           query{
                getFormFieldType{
                    name
                }
            }
        """ 

        response = client.execute(query)
        assert 'errors' not in response

        data = response['data']['getFormFieldType']
        assert data is not None 
    
    def test_get_association_form_filled(self):
        client = Client(schema, context_value=self.req) 
        self.association.slug = "aa-aa"
        self.association.save()
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)
        query = """
           query{
                getAssociationFormFilled(slug:\"%s\"){
                 userPayedCost{user{key}}
                }
            }
        """  %(self.association.slug)

        response = client.execute(query)
        assert 'errors' not in response

        data = response['data']['getAssociationFormFilled']
        assert data is not None 

    def test_get_association_form_filled_by_user(self):
        client = Client(schema, context_value=self.req) 
        self.association.slug = "aa-aa"
        self.association.save()
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)
        query = """
           query{
                getAssociationFormFilledByUser(slug:\"%s\", key:\"%s\"){
                 userPayedCost{user{key}}
                }
            }
        """  %(self.association.slug, self.user.key)

        response = client.execute(query)
        assert 'errors' not in response

        data = response['data']['getAssociationFormFilledByUser']
        assert data is not None 

    
    def test_get_user_accepted_join_request(self):
        client = Client(schema, context_value=self.req) 
        self.association.slug = "aa-aa"
        self.association.save()
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)
        query = """
           query{
                getUserAcceptedJoinRequest(slug:\"%s\"){
                 userPayedCost{user{key}}
                }
            }
        """  %(self.association.slug)

        response = client.execute(query)
        assert 'errors' not in response

        data = response['data']['getUserAcceptedJoinRequest']
        assert data is not None

    def test_get_user_declined_join_request(self):
        client = Client(schema, context_value=self.req) 
        self.association.slug = "aa-aa"
        self.association.save()
        Member.objects.create(user=self.user,
                              association=self.association,
                              is_owner=True)
        query = """
           query{
                getUserDeclinedJoinRequest(slug:\"%s\"){
                 userPayedCost{user{key}}
                }
            }
        """  %(self.association.slug)

        response = client.execute(query)
        assert 'errors' not in response

        data = response['data']['getUserDeclinedJoinRequest']
        assert data is not None

