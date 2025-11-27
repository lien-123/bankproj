from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Account, Payee, Transaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id','account_number','balance','currency','created_at')

class PayeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payee
        fields = ('id','name','account_number','bank_code','created_at')

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id','from_account','to_account_number','to_account_owner_name','amount','fee','status','created_at','completed_at','note','reference')
        read_only_fields = ('status','created_at','completed_at')
