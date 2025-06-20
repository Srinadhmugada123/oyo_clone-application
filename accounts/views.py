from django.shortcuts import render, redirect
from .models import HotelUser, HotelVendor, Hotel
from django.db.models import Q
from django.contrib import messages
from .utils import generateRandomToken, sendEmailToken, sendOTPtoEmail
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
import random
from django.contrib.auth.decorators import login_required
from .utils import generateslug
# Create your views here.
def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        hotel_user = HotelUser.objects.filter(
            email=email)
        
        if not hotel_user.exists():
            messages.warning(request, "No accound found.")
            return redirect('/account/login/')
        
        if not  hotel_user[0].is_verified:
            messages.success(request, "Account not verified")
            return redirect('/account/login/')
        
        hotel_user = authenticate(username = hotel_user[0].username, password= password)
        if hotel_user:
             messages.success(request, "Login successfull")
             login(request, hotel_user)
             return redirect('/account/login/')
        messages.warning(request, "Login Failed. please check your credentials")
        return redirect('/account/login/')


    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        password = request.POST.get('password')

        hotel_user = HotelUser.objects.filter(
            Q(email = email) | Q(phone_number = phone_number) 
        )
        if hotel_user.exists():
            messages.warning(request, "Account exit with email or phone number")
            return redirect('/account/register/')
        hotel_user = HotelUser.objects.create(
            username=first_name,
            first_name = first_name,
            last_name = last_name,
            phone_number = phone_number,
            email= email,
            email_token = generateRandomToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()

        sendEmailToken(email, hotel_user.email_token)

        messages.success(request, "Email sent to your email")
        return redirect('/account/register/')

    return render(request, 'register.html')


def verify_email_token(request, token):
    try:
        hotel_user = HotelUser.objects.get(email_token = token)
        hotel_user.is_verified = True
        hotel_user.save()
        messages.success(request, "Email verified")
        return redirect('/account/login/')

    except Exception as e:
        return HttpResponse("Invalid token")
    



def send_otp(request, email):
    hotel_user = HotelUser.objects.filter(
        email=email)
    if not hotel_user.exists():
        messages.warning(request, "No accound found.")
        return redirect('/account/login/')
    
    otp = random.randint(1000, 9999)
    hotel_user.update(otp = otp)
    sendOTPtoEmail(email, otp)
    email=email
    return redirect(f'/account/verify-otp/{email}/')



def verify_otp(request , email):
    if request.method == "POST":
        otp  = request.POST.get('otp')
        hotel_user = HotelUser.objects.get(email = email)

        if otp == hotel_user.otp:
            messages.success(request, "Login Success")
            login(request , hotel_user)
            return redirect('/account/login/')

        messages.warning(request, "Wrong OTP")
        return redirect(f'/account/verify-otp/{email}/')

    return render(request , 'verify_otp.html')


def login_vendor(request):    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        hotel_user = HotelVendor.objects.filter(
            email = email)


        if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('/account/login-vendor/')

        if not hotel_user[0].is_verified:
            messages.warning(request, "Account not verified")
            return redirect('/account/login-vendor/')

        hotel_user = authenticate(username = hotel_user[0].username , password=password)

        if hotel_user:
            messages.success(request, "Login Success")
            login(request , hotel_user)
            return redirect('/account/dashboard/')

        messages.warning(request, "Invalid credentials")
        return redirect('/account/login-vendor/')
    return render(request, 'vendor/login_vendor.html')

def register_vendor(request):
    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        business_name = request.POST.get('business_name')

        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        hotel_user = HotelUser.objects.filter(
            Q(email = email) | Q(phone_number  = phone_number)
        )

        if hotel_user.exists():
            messages.warning(request, "Account exists with Email or Phone Number.")
            return redirect('/account/register-vendor/')

        hotel_user = HotelVendor.objects.create(
            username = phone_number,
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone_number = phone_number,
            business_name = business_name,
            email_token = generateRandomToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()

        sendEmailToken(email , hotel_user.email_token)

        messages.success(request, "An email Sent to your Email")
        return redirect('/account/register-vendor/')


    return render(request, 'vendor/register_vendor.html')


@login_required(login_url='login_vendor')
def dashboard(request):
    return render(request, 'vendor/vendor_dashboard.html')

@login_required(login_url='login_vendor')
def add_hotel(request):
    if request.method == "POST":
        hotel_name = request.POST.get('hotel-name')
        hotel_description = request.POST.get('hotel_description')
        ameneties = request.POST.get('ameneties')
        hotel_price = request.POST.get('hotel_price')
        hotel_offer_price = request.POST.get('hotel_offer_price')
        hotel_location = request.POST.get('hotel_location')
        hotel_slug = generateslug(hotel_name)

        Hotel.objects.create(
            hotel_name = hotel_name,
            hotel_description = hotel_description,
            hotel_price = hotel_price,
            hotel_offer_price = hotel_offer_price,
            hotel_location = hotel_location,
            hotel_slug = hotel_slug,

        )
        messages.success(request, "Hotel created")
        return redirect('/account/dashboard/')


    return render(request, 'vendor/add_hotel.html')