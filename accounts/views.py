import email
from email.message import EmailMessage
import imp
from django.shortcuts import redirect, render

import accounts
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from accounts.forms import RegistrationForm
from django.http import HttpResponse
# Verification Email 
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Create your views here.




def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST) # request.POST will contaiin all the Fields values.
        if form.is_valid(): # if th e form has all the required fields
            first_name = form.cleaned_data['first_name'] # We need to fetch all the field from this reques POST
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password) # This will create user, we assigned user create in ccounts.models, this will alse verify user with email.
            user.phone_number = phone_number
            user.save()

            # User Activation
            current_site = get_current_site(request)  # Currently we are using LocalHost, it is for future when the site will be live, to check site server
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)), # Encode user data
                'token': default_token_generator.make_token(user), # Check Token
            }) # The message body we send to the user.
           # with base64 we encoding user id. 
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request, 'Thank you for registering with us. We have sent you a verification email to your email address. Please verify it.')
            return redirect('/accounts/login/?command=verification&email='+email) # it will send show message to the user with email in case of correct email received, through the help of browser url.

    else:
        form = RegistrationForm() # It means it is just a GET request, Then the registration chuld render.
    
    context = {
        'form' : form,
    }

    return render(request, 'accounts/register.html', context)

def login(request): # Check Loin function later
    if request.method == 'POST':
        email = request.POST['email'] # email as name='email' inside of inpu field at login.html
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password) # It will authenticate and return user as object

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in!") 
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid login credentials") # Erroe Message
            return redirect('login')

    return render(request, 'accounts/login.html')

@login_required(login_url = "login")
def logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out.")
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode() # This will decode uidb and decode the primary key of the user
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    # Now we check the token
    if user is not None and default_token_generator.check_token(user, token): # This will check user and token
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your acciunt is activated')
        return redirect('login')

    else:
        messages.error(request, 'Invalid activtion link')
        return redirect('register')                
    

@login_required(login_url = "login") # Only show if user is logged in
def dashboard(request):
    return render(request, 'accounts/dashboard.html')



def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists(): # This will give us true of false
            user = Account.objects.get(email__exact=email)

            # User Forgot Passwors Account Activation.
            # Reser PAssword Email  
            current_site = get_current_site(request)  # Currently we are using LocalHost, it is for future when the site will be live, to check site server
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)), # Encode user data
                'token': default_token_generator.make_token(user), # Check Token
            }) # The message body we send to the user.
           # with base64 we encoding user id. 
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')

        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')

    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode() # This will decode uidb and decode the primary key of the user
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token): # This will check user and token (check this is the secure request or not)
        request.session['uid'] = uid # We will take this session later when we will reseting the password.
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')

    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')


def resetPassword(request): # We already have uid in session so there is no need for import.
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password: # Checking the password and confirm password are same or not
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password) # set_password: it is a django function, it will save your password in hash format at django admin and change your password. Just saving your password in dataase will not work.
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')

        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')

    else:
        return render(request, 'accounts/resetPassword.html')