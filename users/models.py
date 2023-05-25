from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("이메일은 필수입니다.")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):

    email = models.EmailField(verbose_name="이메일", max_length=255, unique=True)
    username = models.CharField(max_length=20, null=True)
    profile_image = models.ImageField(blank=True, null=True, upload_to="profile_img")

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    followings = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers", blank=True, verbose_name="팔로워")

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
    