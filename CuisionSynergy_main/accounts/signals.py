from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import User, UserProfile


@receiver(post_save,sender=User)
def post_save_create_profile_receiver(sender,instance,created,**kwargs):
    """
    Signal handler for the `post_save` signal triggered by the User model.

    This function is called after a User instance is saved.
    - If the User instance is newly created, it creates a corresponding UserProfile instance.
    - If the User instance is updated and the UserProfile doesn't exist, it creates one.
      Otherwise, it updates the existing UserProfile.
    """
    if created:
        # Create a UserProfile for the newly created User.
        UserProfile.objects.create(user=instance)
        print("\nuser profile created")
    else:
        try:
            # Attempt to fetch the existing UserProfile and save it.
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # If no UserProfile exists, create a new one.
            UserProfile.objects.create(user=instance)
            print("\nuser profile not exist,so i created new")
        print("\nuser profile updated")


@receiver(pre_save,sender=User)
def pre_save_create_profile_receiver(sender,instance,**kwargs):
    """
    Signal handler for the `pre_save` signal triggered by the User model.

    This function is called before a User instance is saved.
    """
    print(instance.username,"this user being saved")
# post_save.connect(post_save_create_profile_receiver,sender=User)
