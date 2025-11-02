from django.db import models
from django.contrib.auth.models import User

class GlucoseRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    temperature = models.FloatField()
    heart_rate = models.FloatField()
    interbeat_interval = models.FloatField()
    chosen_model = models.CharField(max_length=20)
    predicted_glucose = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.predicted_glucose}"
