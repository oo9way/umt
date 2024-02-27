from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        SALES = "SALES", "Savdo"
        MATERIALS = "MATERIAL", "Material"
        SPARE = "SPARE", "Ehtiyot qism"
        DIRECTOR = "DIRECTOR", "Nazoratchi"
        INACTIVE = "INACTIVE", "Nofaol"

    base_role = Role.ADMIN

    role = models.CharField(max_length=32, choices=Role.choices)
