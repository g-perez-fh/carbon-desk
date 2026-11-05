from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Project user, ready for organisation and role fields in the accounts subsystem."""
