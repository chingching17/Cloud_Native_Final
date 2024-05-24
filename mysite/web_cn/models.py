from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# create a model for todo list
class require_info(models.Model):
    req_id = models.AutoField(primary_key=True)
    factory = models.CharField(max_length=5)
    priority = models.CharField(max_length=15)
    lab = models.CharField(max_length=20)
    current_priority = models.IntegerField()
    status = models.CharField(max_length=20)
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    is_submitted = models.BooleanField(default=False)
    submitted_by = models.ForeignKey(User, related_name='submitted_tasks', on_delete=models.SET_NULL, null=True, blank=True)
    completed_by = models.ForeignKey(User, related_name='completed_tasks', on_delete=models.SET_NULL, null=True, blank=True)
