from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.


class stationDetail(models.Model):
    station = models.CharField(primary_key=True, max_length=5)
    stationName = models.CharField( max_length=50)
    stationPersonelId = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.station

class transactionDetail(models.Model):
    transaction = models.CharField(primary_key=True, max_length=10)
    UserID =models.CharField(max_length=50)
    balance = models.IntegerField()
    transactionAmount = models.IntegerField()
    station = models.ForeignKey(stationDetail, on_delete = models.RESTRICT)
    InOut = models.CharField(max_length=10)
    route_in = models.IntegerField(null=True, blank=True,)
    route_out = models.IntegerField(null=True, blank=True,)
    station_in = models.IntegerField(null=True, blank=True,)
    station_out = models.IntegerField(null=True, blank=True,)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction


class recharge(models.Model):
    recharge = models.CharField(primary_key=True, max_length=10)
    cardId = models.CharField(max_length=50)
    balance = models.IntegerField()
    transactionAmount = models.IntegerField()
    station = models.ForeignKey(stationDetail, on_delete = models.RESTRICT)
    userId = models.ForeignKey(User, on_delete = models.RESTRICT)
    cardStatus = models.CharField(max_length=10)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.recharge


class topUp(models.Model):
    recharge = models.CharField(primary_key=True, max_length=10)
    cardId = models.CharField(max_length=50, null=True)
    balance = models.IntegerField(null=True)
    transactionAmount = models.IntegerField()
    station = models.ForeignKey(stationDetail, on_delete = models.RESTRICT)
    userId = models.ForeignKey(User, on_delete = models.RESTRICT)
    cardStatus = models.CharField(max_length=10, null=True)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.recharge


class UserReg(models.Model):
    id=models.AutoField(primary_key=True)
    Name=models.CharField(max_length=50, blank=True, null=True)
    Email=models.EmailField(blank=True, null=True)
    Gender=models.CharField(max_length=7, blank=True, null=True)
    Phone=models.IntegerField(blank=True, null=True)
    Address=models.CharField(max_length=100, blank=True, null=True)
    Institution=models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.id    


class UserCardRegistration(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    name=models.CharField(max_length=50, blank=True, null=True)
    phone=models.IntegerField(blank=True, null=True)
    card_number=models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20)
    user=models.ForeignKey(User, on_delete = models.RESTRICT)
    station = models.ForeignKey(stationDetail, on_delete = models.RESTRICT)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id


class CardBalance(models.Model):
    id=models.AutoField(primary_key=True)
    balance=models.IntegerField(null=False)
    card=models.ForeignKey(UserCardRegistration, on_delete = models.RESTRICT)
    station = models.ForeignKey(stationDetail, on_delete = models.RESTRICT)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id



#######
# class Facility(models.Model):
#     facility_id = models.AutoField(primary_key=True)
#     facility_name = models.CharField(max_length=255, null=False)


# class Station(models.Model):
#     station_id = models.AutoField(primary_key=True)
#     station_name = models.CharField(max_length=255)
#     facility = models.ForeignKey(Facility, on_delete= models.CASCADE)
#     owner = models.FloatField(User, on_delete=models.RESTRICT)

# class Card(models.Model):
#     card_number = models.CharField(primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.RESTRICT)

