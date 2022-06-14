from rest_framework import serializers
from .models import transactionDetail

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = transactionDetail
        fields = ('transaction','UserID','balance','transactionAmount','station','InOut')


