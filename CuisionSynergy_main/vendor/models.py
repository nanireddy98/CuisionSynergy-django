from django.db import models
from accounts.utils import send_notification_mail

from accounts.models import User, UserProfile


class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100,unique=True)
    vendor_licence = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name

    def save(self, *args, **kwargs):
        """
        Overrides the save method of the Vendor model to send an email notification when there is a change in the approval status of the Vendor
        """
        if self.pk is not None:
            org = Vendor.objects.get(pk=self.pk)
            if org.is_approved != self.is_approved:  # Check if there is a change in the 'is_approved' field

                mail_template = "accounts/emails/admin_approval_email.html"
                mail_subject = "Congratulations! Your Account has been Approved"
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved
                }

                if self.is_approved:
                    send_notification_mail(mail_subject, mail_template, context)
                else:
                    mail_subject = ("We're Sorry! You are not eligible to publish "
                                    "your food menu on our marketplace")
                    send_notification_mail(mail_subject, mail_template, context)

        return super(Vendor, self).save(*args, **kwargs)
