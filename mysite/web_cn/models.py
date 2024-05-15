from django.db import models

# Create your models here.

# create a model for todo list
class require_info(models.Model):
    req_id = models.AutoField(primary_key=True)
    factory = models.CharField(max_length=5)
    priority = models.CharField(max_length=15)
    lab = models.CharField(max_length=20)
