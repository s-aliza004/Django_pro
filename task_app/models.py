from django.db import models
from django.contrib.auth.models import User


class TODO(models.Model):
  

    STATUS_CHOICES = [
        ("C", "Completed"),
        ("P", "Pending"),
    ]
    
    title = models.CharField(max_length=122)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)
    due_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.title