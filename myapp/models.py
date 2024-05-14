from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.    
# model to save PDF history
class PDFHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pdf_histories')
    pdf = models.FileField(upload_to='', blank=True)
    image = models.ImageField(upload_to='', null=True, blank=True)

