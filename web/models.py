from django.db import models

class House(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Appliance(models.Model):
    name = models.CharField(max_length=100)
    house = models.ForeignKey(House, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Program(models.Model):
    name = models.CharField(max_length=100)
    time_in_minutes = models.IntegerField()
    appliance = models.ForeignKey(Appliance, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} ({self.time_in_minutes} minutes)'
