from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

"""Create your models here."""
class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class RequestQuote(TimeStampedModel):
    email = models.EmailField()
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.email
    
    