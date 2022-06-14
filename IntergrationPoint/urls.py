
from django.urls import path
from . import views
from IntergrationPoint.views import* 
# IntergrationPoint
# from django.contrib import admin


urlpatterns = [
    
    path('getData/', views.ReceiveData, name='getData'),
    path('transaction/', views.transactionPage, name="TransactionPage"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('updates/',views.updates_today, name="Updates"),
    path('station_transaction/<id>',views.stationTransaction, name="station_transaction"),
    path('station_topup/<id>',views.stationTopUp, name="station_topup"),
    path('transaction_by_date/<id>',views.stationTransactionDate, name="transaction_by_date"),
    path('auth_login/', views.authLogin, name='auth_login'),
    path('login/', views.login, name="login"),
    path('accounts/login/', views.login, name="login"),
    path('accounts/logout', views.logout, name="logout"),
    path('settingsPage/', views.settingsPage, name="settingsPage"),
    path('universal_home_page', UniversalHomePage.as_view(), name="universal_home_page"),
    path('transaction_rx/', views.transData, name="transactions"),
    path('', UniversalHomePage.as_view(), name="universal_home_page"),
    path('CardRegister', views.CardRegister, name ="CardRegister"),
    path('UserRegister', views.UserRegister, name="UserRegister")
    
    
]
