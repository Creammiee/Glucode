from django.db import models
from django.contrib.auth.models import User

class GlucoseReading(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    glucose_level = models.FloatField()

    def __str__(self):
        return f"{self.user.username} - {self.glucose_level} mg/dL at {self.timestamp}"
