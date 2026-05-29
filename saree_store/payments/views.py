import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from store.models import Order, Cart
from .phonepay import PhonePeGateway

def initiate(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Generate unique transaction id
    transaction_id = f"TXN_{uuid.uuid4().hex[:12].upper()}"
    order.transaction_id = transaction_id
    order.save()
    
    gateway = PhonePeGateway()
    payment_data = gateway.build_payment_request(
        transaction_id=transaction_id,
        user_id=request.user.id if request.user.is_authenticated else None,
        amount_in_rs=order.total_amount,
        order_id=order.id
    )
    
    # We redirect to a premium interactive simulation of PhonePe portal 
    # to keep it "dummy for now" but complete and easily replaceable
    context = {
        'order': order,
        'transaction_id': transaction_id,
        'payment_data': payment_data,
    }
    return render(request, 'payments/mock_gateway.html', context)

@csrf_exempt
def callback(request):
    order_id = request.GET.get('order_id') or request.POST.get('order_id')
    transaction_id = request.GET.get('transaction_id') or request.POST.get('transaction_id')
    status = request.GET.get('status') or request.POST.get('status') or 'SUCCESS'
    
    order = get_object_or_404(Order, id=order_id)
    
    if status == 'SUCCESS':
        order.status = 'Paid'
        order.save()
        
        # Clear Cart
        if request.user.is_authenticated:
            Cart.objects.filter(user=request.user).delete()
        elif request.session.session_key:
            Cart.objects.filter(session_key=request.session.session_key).delete()
            
        return redirect('store:order_success', order_id=order.id)
    else:
        order.status = 'Failed'
        order.save()
        return render(request, 'payments/failed.html', {'order': order})
