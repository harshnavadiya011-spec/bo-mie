from django.db import models

class Role(models.Model):
    role = models.CharField(max_length=100, unique=True)
    permissions = models.JSONField()
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
   