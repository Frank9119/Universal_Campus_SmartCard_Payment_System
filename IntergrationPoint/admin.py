#from gateMiniserver.IntergrationPoint.models import Transaction
from django.contrib import admin
from .models import transactionDetail, stationDetail, recharge, topUp

# Register your models here.


admin.site.register(transactionDetail)
admin.site.register(stationDetail)
admin.site.register(recharge)
admin.site.register(topUp)
