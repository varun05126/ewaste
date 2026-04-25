# ewaste_backend/core/models.py

from django.db import models
from django.contrib.auth.models import User

class PickupRequest(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15) # Changed from phone_number, simplified max_length
    address = models.TextField() # Consolidated address fields into one
    latitude  = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"

# Keep your ContactMessage model as it was:
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} - {self.subject or 'No Subject'}"

    class Meta:
        ordering = ['-submitted_at']