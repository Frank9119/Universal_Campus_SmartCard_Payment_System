from django.db.models.expressions import F, When
from django.db.models.fields import TimeField
from django.http import response
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import timezone, activate, get_current_timezone
from datetime import datetime, date, time, timedelta
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
import datetime as dt
import pytz
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.db.models import Model
from .models import transactionDetail, recharge, topUp, stationDetail, UserCardRegistration, CardBalance
from .serializers import UsersSerializer
from django.views.generic import TemplateView
import requests
import json
from django.core.serializers.json import DjangoJSONEncoder
import string
import random
from .pyserial import comPort
import asyncio
import websockets
import serial
import threading
from csv import writer
from django.contrib.auth.base_user import BaseUserManager
# from .algorithm import deduct


# Create your views here

class UniversalHomePage(TemplateView):  
      template_name = "landing_page/landing.html"


@login_required
def CardRegister(request):
    if request.method == "GET":
        statioName = stationDetail.objects.all()
        
        transactions = {'statioName': statioName}
        print(transactions)
        return render(request,'htmlfiles/register_card.html', {"transactions":statioName})

    if request.method == "POST":
        name = request.POST['name']
        Phone_Number = request.POST['phone_number']
        card_number = request.POST['card_number']
        Status = request.POST['Status']
        Balance = request.POST['Balance']
        station = str(request.POST['station'])

        
        Balance = int(Balance)+1000
        print(station)
        registerCrad = UserCardRegistration(id = card_number,
                                            name=name, 
                                            card_number=card_number,
                                            status = Status,
                                            phone = Phone_Number,
                                            user=request.user,
                                            station_id = station
                                            )
        try:

            registerCrad.save()
        except Exception as e:
            print(e)

        card_balance = CardBalance(
                                    card_id=card_number,
                                    station_id = station,
                                    balance = Balance
                                    )
        try:
            
            card_balance.save()
        except Exception as e:
            print(e)

            messages.success(request, 'Card Details saved Successful')
            print("Response 200 OK! Data Saved Successful")

        except Exception as e:
            messages.error(request, 'Saving Crad Details, Failed')
            print("Save failed")

        return redirect("CardRegister")


def UserRegister(request):
    #return render(request, 'Registration page/UserReg.html')
    if request.method=="POST":
        Name=request.POST['Name']
        Email=request.POST['Email']
        password=BaseUserManager().make_random_password()
        Confirm_Password=request.POST['Confirm_Password']
        Gender=request.POST['Gender']
        Phone=request.POST['Phone']
        Address=request.POST['Address']
        Institution=request.POST['Institution']
        

        if User.objects.filter(Email=Email).exists():
            messages.error(request, 'You have already register but if not, please try to change your Email or contact your adminstrator')
            return HttpResponseRedirect('addofficers')
        else:
            new_user=User.objects.create_user(Name=Name,username=Email,password=password)
            new_user.save()

            get_user_id=User.objects.get(username=Email)
            new_UserRegister=UserRegister()
            new_UserRegister.Gender=Gender
            new_UserRegister.Phone=Phone
            new_UserRegister.Address=Address
            new_UserRegister.Institution=Institution
            new_UserRegister.save()

            messages.success(request, 'User registration is done successfuly')
            return HttpResponseRedirect('landing_page/landing.html')
      
    else:
            return render(request,'Registration page/UserReg.html')

######################################################################################################    
def authLogin(request):
    return render(request, 'user_management/login.html')
    

def login(request):
    if request.user.is_authenticated:

        return redirect("dashboard")
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']

            user = auth.authenticate(username=username, password=password)

            if user is not None:
                auth.login(request, user)
                messages.success(request, 'Login Successful')
                print("Nime-login")
                return redirect("dashboard")

            else:
                messages.error(request, 'Invalid usernae or password')
                return redirect("login")

        elif request.method == "GET":
            return render(request, "user_management/login.html")


def logout(request):
    auth.logout(request)
    messages.success(request, 'User Logout Successful')
    return redirect('universal_home_page')


@login_required
def dashboard(request):
    if request.method == 'GET':
        Intrans,Outrans,trans_all1,trans_all2,TotalTransaction1,TotalTransaction2,topuptotal1 = 0,0,0,0,0,0,0
        transactions = transactionDetail.objects.all().values_list("transaction", "balance","transactionAmount", "station","InOut","time")

        Intransactions = transactions.all().filter(InOut='in').values_list('transactionAmount', flat=True)
        for transaction in Intransactions:
            Intrans = Intrans + transaction

        Outransactions = transactions.all().filter(InOut='out').values_list('transactionAmount', flat=True)
        stationid = stationDetail.objects.all().latest("station")
        statioName = stationDetail.objects.filter(station=stationid).values("stationName")
        statioName = statioName[0]["stationName"]

        for transaction in Outransactions:
            Outrans = Outrans + transaction

        TotalTransaction1 = Intrans + Outrans
        trans_all1 = {'amountIn': Intrans, 'amountOut': Outrans, 'name': statioName, 'total':TotalTransaction1}

        topuptotal = topUp.objects.all().values_list('transactionAmount', flat=True)
        for transaction in topuptotal:
            topuptotal1 = topuptotal1 + transaction


        def yesterdayTransaction(table_name):
            yesterday_date = datetime.today().date() - relativedelta(days=1)
            yesterday_earn = table_name.objects.filter(time__lt = datetime.today().date(), time__gte = yesterday_date).values_list('transactionAmount', flat=True)
            TransactionAmounty = 0
            for Amount in yesterday_earn:
                TransactionAmounty += Amount
            return TransactionAmounty


        def dailyTransaction(table_name):
            daily_earn = table_name.objects.filter(time__gte=datetime.today().date()).values_list('transactionAmount', flat=True)
            TransactionAmount1 = 0
            for Amount in daily_earn:
                TransactionAmount1 += Amount
            return TransactionAmount1

        def weeklyTransaction(table_name):
            today = datetime.now(tz=get_current_timezone())
            end_date = today
            start_date = end_date - relativedelta(days=7)
            weekly_earn = table_name.objects.filter(time__range=(start_date, end_date)).values_list('transactionAmount', flat=True)
            TransactionAmount2 = 0
            for Amount in weekly_earn:
                TransactionAmount2 += Amount
            return TransactionAmount2

        def monthlyTransaction(table_name):
            print(datetime.today().date().month)
            m = datetime.today().date().month
            y = datetime.today().date().year
            monthly_earn = table_name.objects.filter(time__gte=dt.datetime(y, m, 1)).values_list('transactionAmount',flat=True)
            TransactionAmount3 = 0
            for Amount in monthly_earn:
                TransactionAmount3 += Amount
            return TransactionAmount3

        def yearlyTransaction(table_name):
        
            y = datetime.today().date().year
            yearly_earn = table_name.objects.filter(time__gte=dt.datetime(y, 1, 1)).values_list('transactionAmount',flat=True)
            TransactionAmount4 = 0
            for Amount in yearly_earn:
                TransactionAmount4 += Amount
            return TransactionAmount4

        y = datetime.today().date().year
        Intrans2, Outrans2 = 0,0
       
        Intransactions1 = transactions.all().filter(time__gte=dt.datetime(y, 1, 1),InOut='in').values_list('transactionAmount', flat=True)
        for transaction in Intransactions1:
            Intrans2 = Intrans2 + transaction

        Outransactions1 = transactions.all().filter(time__gte=dt.datetime(y, 1, 1), InOut='out').values_list('transactionAmount', flat=True)
        for transaction in Outransactions1:
            Outrans2 = Outrans2 + transaction

        TotalTransaction2 = Intrans2 + Outrans2
        trans_all2 = {'amountIn': Intrans2, 'amountOut': Outrans2, 'name':statioName, 'total':TotalTransaction2}

        TransactionAmount1 = dailyTransaction(transactionDetail)
        TransactionAmounty = yesterdayTransaction(transactionDetail)
        TransactionAmount2 = weeklyTransaction(transactionDetail)
        TransactionAmount3 = monthlyTransaction(transactionDetail)
        TransactionAmount4 = yearlyTransaction(transactionDetail)

        TopUpAmounty = yesterdayTransaction(topUp)
        TopUpAmount1 = dailyTransaction(topUp)
        TopUpAmount2 = weeklyTransaction(topUp)
        TopUpAmount3 = monthlyTransaction(topUp)
        TopUpAmount4 = yearlyTransaction(topUp)

        ThisMonth = dt.datetime.now().strftime("%B")
        ThisYear = dt.datetime.now().strftime("%Y")
        recentdata = [TransactionAmount1, TransactionAmounty, TransactionAmount2, TransactionAmount3, TransactionAmount4]
        recentLabel = ["To day","Yesterday", "7 days Ago", ThisMonth, ThisYear]
        recentdata1 = [Intrans, Outrans, TotalTransaction1,Intrans2, Outrans2, TotalTransaction2]
        recentLabel1 = ["Cafeterial "+ ThisYear, "Block1 shop "+ ThisYear, "Block3 shop "+ ThisYear, "Block6 shop "+ ThisYear, "Total"+ ThisYear,"Cafeterial", "Block1 shop", "Block3 shop", "Block6 shop", "Total"]
        recentdata2 = [TopUpAmount1, TopUpAmounty, TopUpAmount2, TopUpAmount3, TopUpAmount4]
        recentLabel2 = ["To day", "Yesterday", "7 days ago", "This Month", "This Year"]

        return render(request, 'htmlfiles/dashboard.html', {
            'yesterdayTrans': TopUpAmounty,
            'todayTrans': TransactionAmount1,
            'weeklyTrans': TransactionAmount2,
            'monthlyTrans': TransactionAmount3,
            'yearlyTrans': TransactionAmount4,
            'todayTrans1': TopUpAmount1,
            'weeklyTrans1': TopUpAmount2,
            'monthlyTrans1': TopUpAmount3,
            'yearlyTrans1': TopUpAmount4,
            'month': ThisMonth,
            'year': ThisYear,
            'trans_all1': trans_all1,
            'trans_all2': trans_all2,
            'trans_total1': TotalTransaction1,
            'trans_total2': TotalTransaction2,
            'data': recentdata,
            'label':recentLabel,
            'data1': recentdata1,
            'label1':recentLabel1,
            'data2': recentdata2,
            'label2':recentLabel2,
            'topuptotal1':topuptotal1,
        })


@login_required
def stationTransaction(request, id):
    try:
        if request.method == 'GET':
            Intrans, Outrans, totaltransactions = 0,0,0
            transaction_list = transactionDetail.objects.filter(InOut=id).order_by('-transaction')
            Intransactions = transactionDetail.objects.all().filter(InOut=id).values_list('transactionAmount', flat=True)
            for transaction in Intransactions:
                Intrans = Intrans + transaction

            stationid = stationDetail.objects.all().latest("station")
            statioName = stationDetail.objects.filter(station=stationid).values("stationName")
            statioName = statioName[0]["stationName"]

            transactions = {
                "transaction": transaction_list,
                "station":statioName,
                "intrans":Intrans
            }
            return render(request, 'htmlfiles/stationtransaction.html', transactions)
        else:
            pass

    except:
        return redirect('dashboard')


@login_required
def stationTransactionDate(request, id):
    try:
        if id == 'daily':
            transaction_list = transactionDetail.objects.filter(time__gte=datetime.today().date()).values(
                "transaction",
                "UserID",
                "balance",
                "transactionAmount",
                "station__stationName",
                "InOut",
                "time"
            ).order_by('-transaction')

            intransaction = transaction_list.filter(InOut="in").values_list('transactionAmount', flat=True)
            outransaction = transaction_list.filter(InOut="out").values_list('transactionAmount', flat=True)
            Intrans, Outrans, totaltransactions = 0,0,0
            for intran in intransaction:
                Intrans = Intrans+intran

            for outran in outransaction:
                Outrans = Outrans+outran

            stationid = stationDetail.objects.all().latest("station")
            statioName = stationDetail.objects.filter(station=stationid).values("stationName")
            statioName = statioName[0]["stationName"]
            print(":::", statioName)
            totaltransactions = Intrans+Outrans
            transactions = {
                "transaction": transaction_list,
                "station": "Daily",
                "totaltrans": totaltransactions,
                "outrans": Outrans,
                "intrans":Intrans,
                "stationName":statioName
            }

            return render(request, 'htmlfiles/stationTransactionDate.html', transactions)

        elif id == 'weekly':
            today = datetime.now(tz=get_current_timezone())
            end_date = today
            start_date = end_date - relativedelta(days=7)
            transaction_list = transactionDetail.objects.filter(time__range=(start_date, end_date)).values(
                "transaction",
                "UserID",
                "balance",
                "transactionAmount",
                "station__stationName",
                "InOut",
                "time"
            ).order_by('-transaction')
            
            intransaction = transaction_list.filter(InOut="in").values_list('transactionAmount', flat=True)
            outransaction = transaction_list.filter(InOut="out").values_list('transactionAmount', flat=True)
            Intrans, Outrans, totaltransactions = 0,0,0
            for intran in intransaction:
                Intrans = Intrans+intran
            
            for outran in outransaction:
                Outrans = Outrans+outran
            stationid = stationDetail.objects.all().latest("station")
            statioName = stationDetail.objects.filter(station=stationid).values("stationName")
            statioName = statioName[0]["stationName"]

            totaltransactions = Intrans+Outrans
            transactions = {
                "transaction": transaction_list,
                "station": "Weekly",
                "totaltrans": totaltransactions,
                "outrans": Outrans,
                "intrans":Intrans,
                "stationName":statioName
            }
            return render(request, 'htmlfiles/stationTransactionDate.html', transactions)

        elif id == 'monthly':
            m = datetime.today().date().month
            y = datetime.today().date().year
            transaction_list = transactionDetail.objects.filter(time__gte=dt.datetime(y, m, 1,0,0, tzinfo=pytz.UTC)).values(
                "transaction",
                "UserID",
                "balance",
                "transactionAmount",
                "station__stationName",
                "InOut",
                "time"
            ).order_by('-transaction')
            
            intransaction = transaction_list.filter(InOut="in").values_list('transactionAmount', flat=True)
            outransaction = transaction_list.filter(InOut="out").values_list('transactionAmount', flat=True)
            Intrans, Outrans, totaltransactions = 0,0,0
            for intran in intransaction:
                Intrans = Intrans+intran
            
            for outran in outransaction:
                Outrans = Outrans+outran
            stationid = stationDetail.objects.all().latest("station")
            statioName = stationDetail.objects.filter(station=stationid).values("stationName")
            statioName = statioName[0]["stationName"]

            totaltransactions = Intrans+Outrans
            transactions = {
                "transaction": transaction_list,
                "station": "Monthly",
                "totaltrans": totaltransactions,
                "outrans": Outrans,
                "intrans":totaltransactions,
                "stationName":statioName
            }
            return render(request, 'htmlfiles/stationTransactionDate.html', transactions)

        elif id == 'yearly':
            y = datetime.today().date().year
            transaction_list = transactionDetail.objects.filter(time__gte=dt.datetime(y, 1, 1, tzinfo=pytz.UTC)).values(
                "transaction",
                "UserID",
                "balance",
                "transactionAmount",
                "station__stationName",
                "InOut",
                "time"
            ).order_by('-transaction')
            
            intransaction = transaction_list.filter(InOut="in").values_list('transactionAmount', flat=True)
            outransaction = transaction_list.filter(InOut="out").values_list('transactionAmount', flat=True)
            Intrans, Outrans, totaltransactions = 0,0,0
            for intran in intransaction:
                Intrans = Intrans+intran
            
            for outran in outransaction:
                Outrans = Outrans+outran
            stationid = stationDetail.objects.all().latest("station")
            statioName = stationDetail.objects.filter(station=stationid).values("stationName")
            statioName = statioName[0]["stationName"]

            totaltransactions = Intrans+Outrans
            transactions = {
                "transaction": transaction_list,
                "station": "Yearly",
                "totaltrans": totaltransactions,
                "outrans": Outrans,
                "intrans":Intrans,
                "stationName":statioName
            }
            
            return render(request, 'htmlfiles/stationTransactionDate.html', transactions)

    except:

        return redirect('dashboard')


@login_required
def stationTopUp(request, id):
    y = datetime.today().date().year
    # try:
    if request.method == 'GET':
        stationid = stationDetail.objects.all().latest("station")
        statioName = stationDetail.objects.filter(station=stationid).values("stationName")
        statioName = statioName[0]["stationName"]
        if id == 'daily':
            transaction_list = topUp.objects.filter(time__gte=datetime.today().date()).order_by('-time')
            intransaction = transaction_list.values_list('transactionAmount', flat=True)
            Intrans = 0
            for intran in intransaction:
                Intrans = Intrans+intran

            transactions = {
                "transaction": transaction_list,
                "station": "Daily",
                "intrans":Intrans,
                "stationName":statioName
            }
            print(transaction_list)
            return render(request, 'htmlfiles/topuptransaction.html', transactions)

        elif id == 'weekly':
            today = datetime.now(tz=get_current_timezone())
            end_date = today
            start_date = end_date - relativedelta(days=7)
            transaction_list = topUp.objects.filter(time__range=(start_date, end_date)).order_by('-time')
            
            intransaction = transaction_list.values_list('transactionAmount', flat=True)
            Intrans = 0
            for intran in intransaction:
                Intrans = Intrans+intran
            
            transactions = {
                "transaction": transaction_list,
                "station": "Weekly",
                "intrans":Intrans,
                "stationName":statioName
            }
            return render(request, 'htmlfiles/topuptransaction.html', transactions)

        elif id == 'monthly':
            m = datetime.today().date().month
            y = datetime.today().date().year
            transaction_list = topUp.objects.filter(time__gte=dt.datetime(y, m, 1,0,0, tzinfo=pytz.UTC)).order_by('-time')
            
            intransaction = transaction_list.values_list('transactionAmount', flat=True)
            Intrans, Outrans, totaltransactions = 0,0,0
            for intran in intransaction:
                Intrans = Intrans+intran
            transactions = {
                "transaction": transaction_list,
                "station": "Monthly",
                "totaltrans": totaltransactions,
                "outrans": Outrans,
                "intrans":totaltransactions,
                "stationName":statioName
            }
            return render(request, 'htmlfiles/topuptransaction.html', transactions)

        elif id == 'yearly':
                y = datetime.today().date().year
                transaction_list = topUp.objects.filter(time__gte=dt.datetime(y, 1, 1, tzinfo=pytz.UTC)).order_by('-time')
                
                intransaction = transaction_list.values_list('transactionAmount', flat=True)
                Intrans = 0
                for intran in intransaction:
                    Intrans = Intrans+intran

                transactions = {
                    "transaction": transaction_list,
                    "station": "Yearly",
                    "intrans":Intrans,
                    "stationName":statioName
                }
          
                return render(request, 'htmlfiles/topuptransaction.html', transactions)

        else:
            pass

    # except:
    #     return redirect('dashboard')

###############################

@csrf_exempt
def ReceiveData(request):
    
    if request.method == "GET":
        try:
            def id_generator():
                latest_id = str(transactionDetail.objects.latest('transaction'))
                latest_id = 'ST0' + str(int(latest_id[3:]) + 1)
                return latest_id

            transaction = id_generator()
            UserID = request.GET.get("UserID")
            route_number = request.GET.get("route_number")
            station_number = request.GET.get("station_number")
            stationId = request.GET.get("station")
            InOut = request.GET.get("InOut")
            transactionAmount = request.GET.get('transactionAmount')
            print('>>', UserID, stationId, InOut, route_number, station_number,transactionAmount)

            def deduct(card_id, stationId, InOut, route_number, station_number, transactionAmount):
                try:
                    available_balance = CardBalance.objects.filter(card = card_id).values("balance")[0]['balance']
                    status = 1
                    
                   
                    # if (InOut == "Cafe" or InOut == "cafe"):
                    if (InOut == "In" or InOut == "in" or InOut == "Out" or InOut == "out"):
                        print('hey ma the in out',InOut)
                        transactionAmount = int(transactionAmount)
                        print(":in:", available_balance)
                        if available_balance>=transactionAmount:
                            Balance = available_balance - transactionAmount
                            print(":balance:", Balance)


                            try:
                                CardBalance.objects.filter(card = card_id).update(balance = Balance)
                                print(":balance Updated:")
                                status = 1
                            except Exception as e:
                                print(e)
                                status = 3
                                print(":balance not Updated:")
                        else:
                            Balance = available_balance
                            status = 2
                except:
                    pass

                return transactionAmount, Balance, status

            deduction_balance, Balance, status = deduct(UserID, stationId, InOut, route_number, station_number, transactionAmount)


            if (InOut == "in" and status==1):
                print('> in >')
                
                transaction_object = transactionDetail(transaction = transaction, 
                                                UserID=UserID, 
                                                balance=Balance, 
                                                transactionAmount=deduction_balance, 
                                                station_id=stationId, 
                                                InOut=InOut,
                                                route_in = route_number,
                                                station_in = station_number,
                                                route_out = None,
                                                station_out = None
                                                )
                transaction_object.save()
                print('> In Trans Complete >')

                return HttpResponse(status=200)

            elif (InOut == "out" and status==1):

                transaction_object = transactionDetail(transaction = transaction, 
                                                UserID=UserID, 
                                                balance=Balance, 
                                                transactionAmount=deduction_balance, 
                                                station_id=stationId, 
                                                InOut=InOut,  
                                                route_in = None,
                                                station_in = None,
                                                route_out = route_number,
                                                station_out = station_number
                                                )
                transaction_object.save()
                print('> Out Trans Complete >')

                return HttpResponse(status=200)
            elif status ==2:
                print("Balance Not enough")
                return HttpResponse(status=300)

            elif status ==4:
                print("Incomplete Transaction")
                return HttpResponse(status=402)

            else:
                print("Response 400 OK! Card not found")
                return HttpResponse(status=400)


        except Exception as e:
            print(e)
            print("Error occured, Try Again")
            return HttpResponse(status=404)

    else:
        print("Error occured, Try Again")
        return HttpResponse(status=404)




@login_required
def transactionPage(request):
    try:
        Intrans,Outrans = 0,0

        Intransactions = transactionDetail.objects.all().filter(InOut='in').values_list('transactionAmount', flat=True)
        for transaction in Intransactions:
            Intrans = Intrans + transaction

        OutransactionsKiv = transactionDetail.objects.all().filter(InOut='out').values_list('transactionAmount', flat=True)
        for transaction in OutransactionsKiv:
            Outrans = Outrans + transaction

        trans = {'amountIn': Intrans, 'amountOut': Outrans, 'name': 'Kivukoni-Dar-es-Salaam'}

        transaction_list = transactionDetail.objects.all().order_by('-transaction')
        Total = Intrans + Outrans
        transactions = {
            "transaction": transaction_list,
            'trans': trans,
            "total":Total,
        }

        return render(request, 'htmlfiles/transactions.html', transactions)

    except:
        return redirect('TransactionPage')


# source virtualenvironment/udart/bin/activate
@login_required
def updates_today(request):
    if request.method == "POST":
        updates = json.loads(request.body.decode("utf-8"))
        banned_cards = updates[0]
        unbanned_cards = updates[1]


@login_required
def recharge(request):
    if request.method == 'GET':
        today = datetime.now(tz=get_current_timezone())
        end_date = today
        start_date = end_date - relativedelta(days=7)

        recharge_list = recharge.objects.all().order_by('-rechargeId')

        transaction_list = recharge.objects.filter(time__gte=datetime.today().date()).order_by('-recharge')
        todaytransaction = transaction_list.values_list('transactionAmount', flat=True)
        today, thisweek, thismonth, thisyear = 0,0,0,0
        for intran in todaytransaction:
            today = today+intran

        transaction_list1 = recharge.objects.filter(time__range=(start_date, end_date)).order_by('-recharge')

        thisweektrans = transaction_list1.values_list('transactionAmount', flat=True)
        for intran1 in thisweektrans:
            thisweek = thisweek+intran1

        m = datetime.today().date().month
        y = datetime.today().date().year
        transaction_list2 = recharge.objects.filter(time__gte=dt.datetime(y, m, 1,0,0, tzinfo=pytz.UTC)).order_by('-recharge')

        thismonthtrans = transaction_list2.values_list('transactionAmount', flat=True)
        for intran2 in thismonthtrans:
            thismonth = thismonth+intran2

        y = datetime.today().date().year
        transaction_list3 = recharge.objects.filter(time__gte=dt.datetime(y, 1, 1, tzinfo=pytz.UTC)).order_by('-recharge')

        thisyeartrans = transaction_list3.values_list('transactionAmount', flat=True)
        for intran3 in thisyeartrans:
            thisyear = thisyear+intran3


        return render(request, 'htmlfiles/recharge.html', {

                                'recharge': recharge_list,
                                'today':today,
                                'thisweek':thisweek,
                                'thismonth':thismonth,
                                'thisyear':thisyear,

                                })


    elif request.method == 'POST':

        def id_generator():
            latest_id = str(recharge.objects.latest('recharge'))
            latest_id = 'ST01' + str(int(latest_id[4:]) + 1)
            print(latest_id)
            return latest_id

        rechargeId = id_generator()
        cardId = request.POST['cardId']
        cardStatus = request.POST['cardstatus']
        balance = request.POST['balance']
        transactionAmount = request.POST['amount']
        userId = request.POST['agentId']
        station = request.POST['station']

        recharge = recharge(recharge=rechargeId, cardId=cardId, cardStatus=cardStatus, balance=balance, transactionAmount=transactionAmount, userId=userId, station=station)
        recharge.save()
        

        messages.info(request, 'Top Up Successful')
        print("I am passing Here")
        return redirect("recharge")
 


@login_required
def settingsPage(request):
    global port1, serialPort, port2
    if request.method == 'GET':
        stationid = stationDetail.objects.all().latest("station")
        statioName = stationDetail.objects.filter(station=stationid).values("stationName")
        statioName = statioName[0]["stationName"]
        return render(request, 'htmlfiles/settings.html', {'comport': port1, 'statioName':statioName, 'stationID':stationid })

    elif request.method == 'POST':

        return render(request, 'htmlfiles/settings.html', {'comport': port1, })


@csrf_exempt
def transData(request):
    if request.method == "POST":
        transactions = json.loads(request.body.decode("utf-8"))
        for transaction_entry in transactions:
            # print(transaction_entry)
            transaction = transaction_entry["transaction"]
            UserID =transaction_entry["UserID"]
            balance = transaction_entry["balance"]
            transactionAmount = transaction_entry["transactionAmount"]
            station = transaction_entry["station_id"]
            InOut = transaction_entry["InOut"]
            time = transaction_entry["time"]
            transaction = transactionDetail(transaction=transaction, UserID=UserID, balance = balance, station_id=station, transactionAmount=transactionAmount, time=time, InOut=InOut)

            transaction.save()

    return HttpResponse("i dont get it!!")


@csrf_exempt
def topup_data_rx(request):
    if request.method == "POST":
        transactions = json.loads(request.body.decode("utf-8"))
        for transaction_entry in transactions:
            recharge = transaction_entry["recharge"]
            cardId =transaction_entry["cardId"]
            userId =transaction_entry["userId_id"]
            balance = transaction_entry["balance"]
            transactionAmount = transaction_entry["transactionAmount"]
            station = transaction_entry["station_id"]
            cardStatus = transaction_entry["cardStatus"]
            time = transaction_entry["time"]

            topup_transaction = topUp(recharge=recharge, cardId=cardId, balance = balance, station_id=station, transactionAmount=transactionAmount, time=time, userId_id=userId, cardStatus = cardStatus)

            topup_transaction.save()

    return HttpResponse("i dont get it!!")