from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.hashers import check_password, make_password

class Role(models.Model):
    role = models.CharField(max_length=100, unique=True)
    permission = ArrayField(
        base_field=models.CharField(max_length=100),
        default=list,
        blank=True,
    )
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.role
   

class Admin(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)
    status = models.BooleanField(default=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="admins")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.email

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def verify_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False