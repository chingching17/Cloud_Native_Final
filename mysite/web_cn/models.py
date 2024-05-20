from django.db import models

# Create your models here.

# create a model for todo list
class require_info(models.Model):
    req_id = models.AutoField(primary_key=True)
    factory = models.CharField(max_length=5)
    priority = models.CharField(max_length=15)
    lab = models.CharField(max_length=20)
    current_priority = models.CharField(max_length=15)
    status = models.CharField(max_length=20)
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    is_submitted = models.BooleanField(default=False)
