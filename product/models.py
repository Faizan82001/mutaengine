from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.URLField()
    category = models.CharField(max_length=255)
    rating = models.FloatField()

    def __str__(self):
        return self.title
