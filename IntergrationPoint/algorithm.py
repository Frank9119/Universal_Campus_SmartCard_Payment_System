import math
import time
from .models import transactionDetail, recharge, topUp, stationDetail, UserCardRegistration, CardBalance



def deduct(card_id, stationId, InOut, route_number, station_number):
    try:
        available_balance = CardBalance.objects.filter(card = card_id).values("balance")[0]['balance']
        print(":>:", available_balance)
        status = 1
        if (InOut == "In" or InOut == "in"):
            
            deducting_amount=200
            print('nimefika')
            print(":in:", available_balance)
            if available_balance>=deducting_amount:
                Balance = available_balance - deducting_amount
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


        elif (InOut == "out" or InOut == "Out"):

            transactions = transactionDetail.objects.filter(UserID=card_id).values('route_in', 'station_in').latest("time")
            RouteNumberIn = transactions["route_in"]
            station_numberIn = transactions["station_in"]
            print('::::', transactions, RouteNumberIn, station_numberIn)
            route_number_out = route_number
            station_number = station_number
            if RouteNumberIn != None and station_numberIn != None:

                print(":Parameters:", RouteNumberIn, station_numberIn, route_number_out, station_number)
                deducting_amount = deduction_algorithm(int(RouteNumberIn), int(station_numberIn), int(route_number_out), int(station_number))
                print("Algorithm ok", deducting_amount)
                if available_balance>=deducting_amount:
                    Balance = available_balance - deducting_amount
                    print(":balance:", Balance)
                    try:
                        CardBalance.objects.filter(card = card_id).update(balance = Balance)
                        print(":balance Updated:")
                        status = 1
                    except Exception as e:
                        print(e)
                        status = 3
                        print(":balance not Updated:")

                elif deducting_amount ==1:
                    status = 3
                    print(":balance not Updated:")

                else:
                    Balance = available_balance
                    status = 2

            else:
                status = 4
                deducting_amount, Balance = 0, 0
        else:
            
            status = 3
            deducting_amount, Balance = 0, 0
            print("Receipt weird inout ")

    except Exception as e:
        print("The card_ doesn't exist")
        status = 3
        deducting_amount, Balance = 0, 0

    return deducting_amount, Balance, status



def deduction_amount_func(hopdiff):

    if (hopdiff ==0 or hopdiff ==1 or hopdiff ==2):
        deducting_amount =0

    elif (hopdiff ==3 or hopdiff ==4 or hopdiff ==5):
        deducting_amount =100

    elif (hopdiff ==6 or hopdiff ==7 or hopdiff ==8):
        deducting_amount =200

    else:
        deducting_amount =400

    return deducting_amount



def deduction_algorithm(RouteNumberIn, station_numberIn, route_number_out, station_number):

    exchange12, exchange13, exchange23, exchange34, exchange35, exchange45 = 6, 6, 8, 8, 8, 8

    if( RouteNumberIn == route_number_out ):
        print("1>>>>")
        hopdiff = abs(station_number - station_numberIn)
    
        deducting_amount = deduction_amount_func(hopdiff)

    
    elif((RouteNumberIn==1 and route_number_out==2) or (RouteNumberIn==2 and route_number_out==1)):
    
        hopdiff = abs(station_number- exchange12)+ abs(station_numberIn-exchange12)
        
        deducting_amount = deduction_amount_func(hopdiff)

    

    elif((RouteNumberIn==1 and route_number_out==3) or (RouteNumberIn==3 and route_number_out==1)):
    
        hopdiff = abs(station_number- exchange13)+ abs(station_numberIn-exchange13)
        
        deducting_amount = deduction_amount_func(hopdiff)

    
    elif((RouteNumberIn==2 and route_number_out==3) or (RouteNumberIn==3 and route_number_out==2)):
    
        hopdiff = abs(station_number - exchange23)+ abs(station_numberIn - exchange23)
        
        deducting_amount = deduction_amount_func(hopdiff)

    
    elif((RouteNumberIn==3 and route_number_out==4) or (RouteNumberIn==4 and route_number_out==3)):
    
        hopdiff = abs(station_number - exchange34)+ abs(station_numberIn - exchange34)
        
        deducting_amount = deduction_amount_func(hopdiff)

    
    elif((RouteNumberIn==3 and route_number_out==5) or (RouteNumberIn==5 and route_number_out==3)):
    
        hopdiff = abs(station_number - exchange35)+ abs(station_numberIn - exchange35)
        
        deducting_amount = deduction_amount_func(hopdiff)

    
    elif((RouteNumberIn==4 and route_number_out==5) or (RouteNumberIn==5 and route_number_out==4)):
    
        hopdiff = abs(station_number - exchange45)+ abs(station_numberIn - exchange45)
        
        deducting_amount = deduction_amount_func(hopdiff)

    
    # //////////////1--4///////////
    
    elif(RouteNumberIn==1 and route_number_out==4):
    
        hopdiff = abs(station_number - exchange34)+ 2 + abs(station_numberIn - exchange13)
        
        deducting_amount = deduction_amount_func(hopdiff)

    
    elif(RouteNumberIn==4 and route_number_out==1):
    
        hopdiff = abs(station_number - exchange13)+ 2 + abs(station_numberIn - exchange34)
        
        deducting_amount = deduction_amount_func(hopdiff)


    # ///////////////1--5//////////
    elif(RouteNumberIn==1 and route_number_out==5):
    
        hopdiff = abs(station_number - exchange35)+ 2 + abs(station_numberIn - exchange13)
        
        deducting_amount = deduction_amount_func(hopdiff)

    
    elif(RouteNumberIn==5 and route_number_out==1):
    
        hopdiff = abs(station_number - exchange13)+ 2 + abs(station_numberIn - exchange35)
        
        deducting_amount = deduction_amount_func(hopdiff)


    # ///////////////2--4//////////

    elif(RouteNumberIn==2 and route_number_out==4):
    
        hopdiff = abs(station_number - exchange34)+ 2 + abs(station_numberIn - exchange23)
        
        deducting_amount = deduction_amount_func(hopdiff)

    
    elif(RouteNumberIn==4 and route_number_out==2):
    
        hopdiff = abs(station_number - exchange23)+ 2 + abs(station_numberIn - exchange34)
        
        deducting_amount = deduction_amount_func(hopdiff)


    # ///////////////2--5//////////

    elif(RouteNumberIn==2 and route_number_out==5):
    
        hopdiff = abs(station_number - exchange35)+ 2 + abs(station_numberIn - exchange23)
        
        deducting_amount = deduction_amount_func(hopdiff)

    
    elif(RouteNumberIn==5 and route_number_out==2):
    
        hopdiff = abs(station_number - exchange23)+ 2 + abs(station_numberIn - exchange35)
        
        deducting_amount = deduction_amount_func(hopdiff)
    
    else:
        deducting_amount = 1

    return deducting_amount

        

#############################
# @csrf_exempt
# def ReceiveData(request):
    
#     if request.method == "GET":
#         try:
#             def id_generator():
#                 latest_id = str(transactionDetail.objects.latest('transaction'))
#                 latest_id = 'ST0' + str(int(latest_id[3:]) + 1)
#                 return latest_id

#             transaction = id_generator()
#             UserID = request.GET.get("UserID")
#             route_number = request.GET.get("route_number")
#             station_number = request.GET.get("station_number")
#             stationId = request.GET.get("station")
#             InOut = request.GET.get("InOut")
#             print('>>', UserID, stationId, InOut, route_number, station_number)
#             deduction_balance, Balance, status = deduct(UserID, stationId, InOut, route_number, station_number)
#             if (InOut == "in" and status==1):
#                 print('> in >')
                
#                 transaction_object = transactionDetail(transaction = transaction, 
#                                                 UserID=UserID, 
#                                                 balance=Balance, 
#                                                 transactionAmount=deduction_balance, 
#                                                 station_id=stationId, 
#                                                 InOut=InOut,
#                                                 route_in = route_number,
#                                                 station_in = station_number,
#                                                 route_out = None,
#                                                 station_out = None
#                                                 )
#                 transaction_object.save()
#                 print('> In Trans Complete >')

#                 return HttpResponse(status=200)

#             elif (InOut == "out" and status==1):

#                 transaction_object = transactionDetail(transaction = transaction, 
#                                                 UserID=UserID, 
#                                                 balance=Balance, 
#                                                 transactionAmount=deduction_balance, 
#                                                 station_id=stationId, 
#                                                 InOut=InOut,  
#                                                 route_in = None,
#                                                 station_in = None,
#                                                 route_out = route_number,
#                                                 station_out = station_number
#                                                 )
#                 transaction_object.save()
#                 print('> Out Trans Complete >')

#                 return HttpResponse(status=200)
#             elif status ==2:
#                 print("Balance Not enough")
#                 return HttpResponse(status=300)

#             elif status ==4:
#                 print("Incomplete Transaction")
#                 return HttpResponse(status=402)

#             else:
#                 print("Response 400 OK! Card not found")
#                 return HttpResponse(status=400)


#         except Exception as e:
#             print(e)
#             print("Error occured, Try Again")
#             return HttpResponse(status=404)

#     else:
#         print("Error occured, Try Again")
#         return HttpResponse(status=404)
