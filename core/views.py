from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import Account, Payee, Transaction
from .serializers import AccountSerializer, PayeeSerializer, TransactionSerializer
from django.db import transaction as db_transaction
from django.utils import timezone
from decimal import Decimal
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt



# -------------------
# Token Login API
# -------------------
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response({"detail": "login success", "token": token.key})
    return Response({"detail": "invalid credentials"}, status=400)


# -------------------
# Logout API (just delete token)
# -------------------
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_logout(request):
    request.user.auth_token.delete()
    return Response({"detail": "logged out"})


# -------------------
# List accounts for logged in user
# -------------------
class AccountListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)


# -------------------
# List payees for logged in user
# -------------------
class PayeeListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PayeeSerializer

    def get_queryset(self):
        return Payee.objects.filter(owner=self.request.user)


# -------------------
# Transfer API
# -------------------
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def transfer_to_payee(request):
    user = request.user
    from_account_id = request.data.get('from_account_id')
    payee_id = request.data.get('payee_id')
    amount = request.data.get('amount')

    try:
        amount = Decimal(str(amount))
        if amount <= 0:
            return Response({"detail":"amount must be > 0"}, status=400)
    except:
        return Response({"detail":"invalid amount"}, status=400)

    # Fetch accounts
    try:
        from_account = Account.objects.select_for_update().get(id=from_account_id, user=user)
    except Account.DoesNotExist:
        return Response({"detail":"from account not found"}, status=404)

    try:
        payee = Payee.objects.get(id=payee_id, owner=user)
    except Payee.DoesNotExist:
        return Response({"detail":"payee not found or not your payee"}, status=404)

    # Check balance
    if from_account.balance < amount:
        return Response({"detail":"insufficient balance"}, status=400)

    # Perform transfer
    with db_transaction.atomic():
        from_account.balance -= amount
        from_account.save()

        try:
            to_account = Account.objects.select_for_update().get(account_number=payee.account_number)
            to_account.balance += amount
            to_account.save()
            to_acc_num = to_account.account_number
            to_owner_name = to_account.user.username
        except Account.DoesNotExist:
            to_acc_num = payee.account_number
            to_owner_name = payee.name

        tx = Transaction.objects.create(
            from_account=from_account,
            to_account_number=to_acc_num,
            to_account_owner_name=to_owner_name,
            amount=amount,
            status='success',
            completed_at=timezone.now(),
            note=request.data.get('note',''),
        )

    return Response({
        "detail":"transfer success",
        "new_balance": str(from_account.balance),
        "transaction": TransactionSerializer(tx).data
    })


# -------------------
# Serve frontend
# -------------------
def index(request):
    return render(request, 'index.html')
