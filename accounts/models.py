from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager



class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    username = models.CharField(max_length=100, unique=True)
    biography = models.TextField(blank=True, null=True)
    joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_influencer = models.BooleanField(default=False)
    profile = models.ImageField(upload_to='#', blank=True, null=True)
    logo = models.ImageField(upload_to='#', blank=True, null=True)
    instagram = models.URLField(blank=True, null=True, unique=True)
    youtube = models.URLField(blank=True, null=True, unique=True)
    twitter = models.URLField(blank=True, null=True, unique=True)
    facebook = models.URLField(blank=True, null=True, unique=True)
    linkedin = models.URLField(blank=True, null=True, unique=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['email'] # just for createsuperuser command

    objects = UserManager()

    class Meta:
        ordering = ['username']

    def fullname(self):
        return f'{self.firstname} {self.lastname}'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin    

class OtpCode(models.Model):
    email = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=5)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.email} - {self.code} - {self.created}'

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'
        
    def __str__(self):
        return f'{self.name}'


class Product(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)
    price = models.PositiveIntegerField()
    image = models.ImageField(upload_to='#', blank=True, null=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.name



class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-balance']

    def __str__(self):
        return f'{self.user} - wallet'



class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    shaba = models.CharField(max_length=24, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    amount = models.PositiveIntegerField()
    status = models.BooleanField(default=None, blank=True, null=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.wallet} - {self.amount}'
