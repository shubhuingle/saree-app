from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/<int:order_id>/', views.initiate, name='initiate'),
    path('callback/', views.callback, name='callback'),
]
