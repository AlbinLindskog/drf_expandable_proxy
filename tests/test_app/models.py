from django.db import models


class Flavor(models.Model):
    flavor = models.CharField(max_length=100)


class Scoop(models.Model):
    size = models.IntegerField()
    flavor = models.ForeignKey('Flavor', on_delete=models.PROTECT)
    ice_cream = models.ForeignKey('Icecream', on_delete=models.CASCADE, related_name='scoops')


class IceCream(models.Model):
    with_waffle = models.BooleanField(default=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='icecreams')


class Order(models.Model):
    paid = models.BooleanField(default=False)
