from django.db import models
from django.utils.translation import ugettext_lazy as _
from accounts.models import BaseUser, Association, AssociationMembership, AssociationGroupMember, Member, AssociationGroup
from phonenumber_field.modelfields import PhoneNumberField

class Form(models.Model):
    association  = models.ForeignKey(Association, verbose_name=_("association"), on_delete=models.CASCADE)
    title =  models.CharField(_("form title"), max_length=125 )
    description = models.TextField(_("form description"),max_length=250)
    email = models.EmailField(_("form email"), max_length = 254)
    photo = models.ImageField(_("form image"),upload_to='associations/forms', blank=True ,null=True)
    phone_number = PhoneNumberField(_("phone number"), null=True)
    link = models.URLField(_("website link"),null=True, blank=True)
    start_date = models.DateField(_("day when form is gonna be available"))
    days = models.IntegerField(_("how many days this form is gonna be available"))
    add_to_request = models.BooleanField(_("Add user to join request"), default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

class Costs(models.Model):
    form = models.ForeignKey(Form, verbose_name=_("cost form"), on_delete=models.CASCADE)
    title = models.TextField(_("payment description"), max_length=50, null=True, blank=False)
    description = models.TextField(_("payment description"), max_length=225)
    amount  = models.FloatField(_("amount must be payed"), )    
    membership_time = models.IntegerField(_("membership time when a user pay this amount"), null=True, blank=False)
    show_in_form  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

class UserPayedCosts(models.Model):
    cost  = models.ForeignKey(Costs, verbose_name=_("cost payed"), on_delete=models.CASCADE)
    user = models.ForeignKey(BaseUser, verbose_name=_("user who payed ths cost"), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def save(self, *args, **kwargs):
        already_payed = UserPayedCosts.objects.filter(cost__form=self.cost.form, user=self.user).exists()
        if already_payed : 
            raise Exception("You only allowed to choose a one cost per form")
        
        # a user who already payed the cost and he is in the association join request list
        already_payed_and_in_join_req = JoinRequest.objects.filter(user_payed_cost__cost=self.cost, user_payed_cost__user=self.user ).exists()
        if already_payed : 
            raise Exception("You are already in the join requests of this association")

        # a user who is already a member
        already_payed_and_member  = Member.objects.filter(user=self.user, is_archived=False).exists()
        if already_payed_and_member :
            raise Exception("You are already a member in this association")

        super().save(*args, **kwargs)
class JoinRequest(models.Model):
    user_payed_cost = models.ForeignKey(UserPayedCosts, verbose_name=_("user payed cost"), on_delete=models.CASCADE, null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    accept = models.BooleanField(_("accept this join request"), default=False)
    updated_at = models.DateTimeField(auto_now=True, null=True)

class FieldType(models.Model):
    name = models.CharField("field name", max_length=125)
    html_name  = models.SlugField("html field name", max_length=225, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

class Choice(models.Model):
    text = models.CharField(_("choice text"), max_length=125)
    name  = models.CharField(_("choice html name or value"), max_length=125)

class Field(models.Model):
    form = models.ForeignKey(Form, verbose_name=_("form"), on_delete=models.CASCADE)
    label = models.CharField("field label", max_length=125)
    name  = models.SlugField("field name", max_length=125, null=True, blank=False)
    description = models.TextField("field description", max_length=500)
    placeholder = models.CharField("field placeholder", max_length=125)
    choices = models.ManyToManyField(Choice)
    show_in_form = models.BooleanField("show field in form", default=True)
    required =  models.BooleanField("field required", default=True)
    type = models.ForeignKey(FieldType, verbose_name=_("field type"), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
   
        
        
        

      
class  FieldData(models.Model):
    field = models.OneToOneField(Field, verbose_name=_("field"), on_delete=models.CASCADE)
    user =  models.ForeignKey(BaseUser, verbose_name=_("user field"), on_delete=models.CASCADE)
    data = models.JSONField(verbose_name=_("field data"))
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

class FormFilledByUser(models.Model):
    user_payed_cost = models.OneToOneField(UserPayedCosts, verbose_name=_("user payed cost"), on_delete=models.CASCADE, null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):

        #check for the required fields
        fields = Field.objects.filter(form=self.user_payed_cost.cost.form, show_in_form=True, required=True)
        for field in fields:
            field_data = FieldData.objects.get(field=field)
            if not field_data.data:
                raise Exception(" this field {} is required".format(field.Label))
        if self.user_payed_cost.cost.form.add_to_request:
             JoinRequest.objects.create(user_payed_cost=self.user_payed_cost)
        else:
            member = Member.objects.create(user=self.user_payed_cost.user, association=self.user_payed_cost.cost.form.association)        
            AssociationMembership.objects.create(membership_time=self.user_payed_cost.cost.membership_time, member=member)


        super().save(*args, **kwargs)

class AssociationGroupJoinRequest(models.Model):
    group = models.ForeignKey(AssociationGroup, verbose_name=_("group"), on_delete=models.CASCADE)
    user_payed_cost = models.ForeignKey(UserPayedCosts, verbose_name=_("user payed cost"), on_delete=models.CASCADE)
    accept = models.BooleanField(_("accept this join request"), default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        group_member_exists = AssociationGroupMember.objects.filter(
                member__user=self.user_payed_cost.user, group=self.group).exists()
        if group_member_exists :
            raise Exception(" You can not join group multiple time")

    
        super().save(*args, **kwargs)
        