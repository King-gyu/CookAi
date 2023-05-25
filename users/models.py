from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.exceptions import ValidationError

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError("이메일은 필수입니다.")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            name=name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    class Meta:
        db_table = "User"
    
    email = models.EmailField(verbose_name="이메일", max_length=255, unique=True,)
    name = models.CharField(verbose_name="이름", max_length=20)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    followings = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers", blank=True, verbose_name="팔로워")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        db_table = "User"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin