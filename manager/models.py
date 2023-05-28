from django.db import models

# Create your models here.
class Manager(models.Model):
    class Meta:
        db_table = 'manager'

    def __str__(self):
        return self.name
