from django.db import models
from accounts.utils import send_notification_mail
from datetime import time, datetime, date

from accounts.models import User, UserProfile


class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_licence = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name

    def is_open(self):
        today = date.today().isoweekday()
        current_day_opening_hours = OpeningHour.objects.filter(vendor=self, day=today)
        current_time = datetime.now().strftime("%H:%M:%S")
        is_open = None
        for i in current_day_opening_hours:
            if not i.is_closed:
                start = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
                end = str(datetime.strptime(i.to_hour, "%I:%M %p").time())
                if start < current_time < end:
                    is_open = True
                    break
                else:
                    is_open = False
        return is_open

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


DAYS = [
    (1, "Monday"),
    (2, "Tuesday"),
    (3, "Wednesday"),
    (4, "Thursday"),
    (5, "Friday"),
    (6, "Saturday"),
    (7, "Sunday"),
]

HOURS_OF_DAY_24 = [(time(h, m).strftime("%I:%M %p"), time(h, m).strftime("%I:%M %p")) for h in range(0, 24) for m in
                   (0, 30)]


class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOURS_OF_DAY_24, max_length=10, unique=True)
    to_hour = models.CharField(choices=HOURS_OF_DAY_24, max_length=10, unique=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', '-from_hour')
        unique_together = ('vendor', 'day', 'from_hour', 'to_hour')

    def __str__(self):
        return self.get_day_display()
