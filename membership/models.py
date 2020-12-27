from django.db import models
from django.utils.translation import ugettext_lazy as _
from accounts.models import BaseUser, Association, AssociationMembership, Member
from phonenumber_field.modelfields import PhoneNumberField
class Form(models.Model):
    association  = models.ForeignKey(Association, verbose_name=_("association"), on_delete=models.CASCADE)
    title =  models.CharField(_("form title"), max_length=125 )
    description = models.TextField(_("form description"),max_length=250)
    email = models.EmailField(_("form email"), max_length = 254)
    photo = models.ImageField(_("form image"),upload_to='associations/forms', blank=True ,null=True)
    phone_number = PhoneNumberField(_("phone number"), null=True)
    link = models.URLField(_("website link"),null=True)
    start_date = models.DateField(_("day when form is gonna be available"))
    days = models.IntegerField(_("how many days this form is gonna be available"))
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

class Costs(models.Model):
    form = models.ForeignKey(Form, verbose_name=_("cost form"), on_delete=models.CASCADE)
    description = models.TextField(_("payment description"), max_length=225)
    amount  = models.FloatField(_("amount must be payed"), )    
    membership_time = models.DurationField(_("membership time when a user pay this amount"), null=True, blank=True)
    show_in_form  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

class UserPayedCosts(models.Model):
    cost  = models.ForeignKey(Costs, verbose_name=_("cost payed"), on_delete=models.CASCADE)
    user = models.ForeignKey(BaseUser, verbose_name=_("user who payed ths cost"), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class FieldType(models.Model):
    name  = models.CharField("field name", max_length=125)


class Field(models.Model):
    form = models.ForeignKey(Form, verbose_name=_("form"), on_delete=models.CASCADE)
    label = models.CharField("field label", max_length=125)
    description = models.TextField("field description", max_length=500)
    placeholder = models.CharField("field placeholder", max_length=125)
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
    user_payed_cost = models.ForeignKey(UserPayedCosts, verbose_name=_("user payed cost"), on_delete=models.CASCADE, null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        fields = Field.objects.filter(form=self.user_payed_cost.cost.form, show_in_form=True, required=True)
        for field in fields:
            field_data = FieldData.objects.get(field=field)
            
        member = Member.objects.create(user=self.user_payed_cost.user, association=self.user_payed_cost.cost.form.association)        
        AssociationMembership.objects.create(membership_time=self.user_payed_cost.cost.membership_time, member=member)


        super().save(*args, **kwargs)
