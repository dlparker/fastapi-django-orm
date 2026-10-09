from django.db import models


# Sample Client model
class Client(models.Model):
    name = models.CharField(max_length=50, default="Dan")

    def __str__(self):
        return self.name
