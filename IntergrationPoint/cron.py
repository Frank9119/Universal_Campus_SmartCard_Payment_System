from django.utils.timezone import timezone, activate, get_current_timezone
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.db.models import Model
from .models import transactionDetail, topUp
import requests
import json
from django.core.serializers.json import DjangoJSONEncoder


def cron():
        end_date = datetime.now(tz=get_current_timezone())
        start_date = end_date - relativedelta(months=1)
        instance = transactionDetail.objects.filter(time__range=(start_date, end_date)).values()

        transaction_list=[]
        for transaction in instance:
                transaction_list.append(transaction)
        transaction_list = json.dumps(transaction_list, cls=DjangoJSONEncoder)
        print(transaction_list)
        requests.post('http://172.17.17.33:8002/transaction_rx/', data=transaction_list)
        return HttpResponse("done!")

def cronTopup():
        end_date = datetime.now(tz=get_current_timezone())
        start_date = end_date - relativedelta(months=1)
        instance = topUp.objects.filter(time__range=(start_date, end_date)).values()

        topup_list=[]
        for topups in instance:
                topup_list.append(topups)
        topup_list = json.dumps(topup_list, cls=DjangoJSONEncoder)
        print(topup_list)
        requests.post('http://172.17.17.33:8002/topup_rx/', data=topup_list)
        return HttpResponse("done!")
