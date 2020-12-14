from django.db import models
from django.utils.translation import ugettext_lazy as _
from accounts.models import BaseUser, Association, AssociationMembership, Member
class Form(models.Model):
    association  = models.ForeignKey(Association, verbose_name=_("association"), on_delete=models.CASCADE)
    title =  models.CharField(_("form title"), max_length=125 )
    description = models.TextField(_("form description"),max_length=250)
    email = models.EmailField(_("form email"))
    start_date = models.DateField(_("day when form is gonna be available"))
    days = models.IntegerField(_("how many days this form is gonna be available"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Costs(models.Model):
    form = models.ForeignKey(Form, verbose_name=_("cost form"), on_delete=models.CASCADE)
    description = models.TextField(_("payment description"), max_length=225)
    amount  = models.FloatField(_("amount must be payed"), )    
    membership_time = models.DurationField(_("membership time when a user pay this amount"), null=True, blank=True)
    show_in_form  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
class UserPayedCosts(models.Model):
    cost  = models.ForeignKey(Costs, verbose_name=_("cost payed"), on_delete=models.CASCADE)
    user = models.ForeignKey(BaseUser, verbose_name=_("user who payed ths cost"), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def create(self, *args, **kwargs):
        member = Member.objects.create(user=self.user, association=self.cost.form.association)
        AssociationMembership.objects.create(membership_time=self.cost.membership_time, member=member)

        super().create(*args, **kwargs)