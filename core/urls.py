from django.urls import path
from .views import api_login, api_logout, AccountListView, PayeeListView, transfer_to_payee, index, TransactionListView

urlpatterns = [
    path('', index, name='index'),  # 這裡對應 index.html
    path('api/login/', api_login),
    path('api/logout/', api_logout),
    path('api/accounts/', AccountListView.as_view()),
    path('api/payees/', PayeeListView.as_view()),
    path('api/transfer/', transfer_to_payee),
    path('api/transactions/', TransactionListView.as_view()),
]
