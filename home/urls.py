from django.urls import path
from home import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hotel-details/<slug>/', views.hotel_details, name="hotel_details")
]
