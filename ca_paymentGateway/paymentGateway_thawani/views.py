from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect,HttpResponse
from .models import Course, CourseRegistration
from django.shortcuts import render, redirect
from .models import Course, CourseRegistration
from django.conf import settings
'''
def register(request):
    courses = Course.objects.all()
    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        civil_id = request.POST['civil_id']
        discount_code = request.POST.get('discount_code', '')
        gender = request.POST['gender']
        category = request.POST['category']
        course_id = request.POST['course']
        course = Course.objects.get(id=course_id)
        
        registration = CourseRegistration(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            civil_id=civil_id,
            discount_code=discount_code,
            gender=gender,
            category=category,
            course=course
        )
        registration.save()
        return redirect('success')
    return render(request, 'courseRegistration.html', {'courses': courses})



def success(request):
    return render(request, 'success.html')
'''
# views2.py
'''

def register(request):
    courses = Course.objects.all()
    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        civil_id = request.POST['civil_id']
        discount_code = request.POST.get('discount_code', '')
        gender = request.POST['gender']
        category = request.POST['category']
        course_id = request.POST['course']
        course = Course.objects.get(id=course_id)
        
        # Calculate total amount based on the selected course (you may have your own logic here)
        total_amount = course.price
        
        # Create registration record in your database
        registration = CourseRegistration.objects.create(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            civil_id=civil_id,
            discount_code=discount_code,
            gender=gender,
            category=category,
            course=course
        )

        # Construct Thwani payment URL
        payment_url = construct_payment_url(registration.id, total_amount)
        
        # Redirect the user to the Thwani payment page
        return redirect(payment_url)

    return render(request, 'courseRegistration.html', {'courses': courses})

from django.conf import settings

def construct_payment_url(registration_id, total_amount):
    api_key = getattr(settings, 'THWANI_API_KEY', '')  # Retrieve your Thwani API key from settings
    return f'https://thawani.om/payment?registration_id={registration_id}&amount={total_amount}&api_key={api_key}'

# views.py

from django.http import HttpResponse
from .models import CourseRegistration

def payment_callback_view(request):
    # Extract callback data (e.g., registration ID, payment status) from request
    registration_id = request.GET.get('registration_id')
    payment_status = request.GET.get('status')

    # Retrieve the registration from your CourseRegistration model
    registration = CourseRegistration.objects.get(id=registration_id)

    # Update registration status based on payment status received from Thwani callback
    if payment_status == 'success':
        registration.status = 'paid'
    elif payment_status == 'pending':
        registration.status = 'pending'
    else:
        registration.status = 'failed'
    
    # Save the updated registration status
    registration.save()

    # Return a response to acknowledge receipt of callback
    return HttpResponse('Callback received and registration status updated.')
'''


'''
import requests
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import Course, CourseRegistration

def register(request):
    courses = Course.objects.all()
    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        civil_id = request.POST['civil_id']
        discount_code = request.POST.get('discount_code', '')
        gender = request.POST['gender']
        category = request.POST['category']
        course_id = request.POST['course']
        course = Course.objects.get(id=course_id)
        
        registration = CourseRegistration(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            civil_id=civil_id,
            discount_code=discount_code,
            gender=gender,
            category=category,
            course=course
        )
        registration.save()

        # Prepare the order payload
        order = prepare_data(request)
        
        # Call the checkout function to create the checkout session
        return checkout(order)

    return render(request, 'courseRegistration.html', {'courses': courses})

def checkout(order):
    # Thwani API endpoint for creating checkout sessions
    api_endpoint = 'https://uatcheckout.thawani.om/api/v1/checkout/session'

    # Secret key for Thwani API authentication
    secret_key = 'rRQ26GcsZzoEhbrP2HZvLYDbn9C9et'

    # Set request headers with the secret key
    headers = {
        'thawani-api-key': secret_key,
        'Content-Type': 'application/json'
    }

    # Make a POST request to create the checkout session
    response = requests.post(api_endpoint, headers=headers, json=order)

    # Check if the request was successful
    if response.status_code == 200:
        try:
            # Parse the JSON response and extract the session ID
            session_id = response.json()['data']['session_id']
        except (KeyError, ValueError):
            return HttpResponse('Failed to create checkout session')

        # Publishable key for Thwani API
        publishable_key = 'HGVTMLDss3ghr9t1N9gr4DVYt0qyBy'

        # Construct the URL for redirecting the user to the payment page
        payment_url = f'https://uatcheckout.thawani.om/pay/{session_id}?key={publishable_key}'

        # Redirect the user to the payment page
        return redirect(payment_url)
    else:
        # Handle the case when creating the checkout session fails
        return HttpResponse('Failed to create checkout session')

def prepare_data(request):
    full_name = request.POST['full_name']
    amount = Course.objects.get(id=request.POST['course']).price
    order = {
        'client_reference_id': '1234KK',  # Generate a unique identifier
        'mode': 'payment',  # Mode of the checkout session
        'products': [
            {
                'name': request.POST['course'],  # Name of the product
                'unit_amount': str(amount),  # Unit amount (in baisa) per line product
                'quantity': 1  # Quantity of the line product
            }
        ],
        'customer_id': request.POST['civil_id'],  # Provide customer ID if available
        'success_url': '/success/',  # Redirect URL after successful payment
        'cancel_url': '/wrong/',  # Redirect URL if payment is canceled
        'save_card_on_success': False,  # Option to save card on success
        'expire_in_minutes': 1440,  # Custom expiry for the session (24 hours)
        'metadata': {
            'full_name': full_name,
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'civil_id': request.POST['civil_id'],
            'discount_code': request.POST.get('discount_code', ''),
            'gender': request.POST['gender'],
            'category': request.POST['category'],
            # Add other metadata as needed
        }
    }
    return order
def success(request):
    return render(request, 'success.html')
def field(request):
    return render(request, 'field.html')
'''

import json
import requests
from django.shortcuts import render, redirect
from .models import Course, CourseRegistration
from django.conf import settings

THAWANI_API_KEY = 'rRQ26GcsZzoEhbrP2HZvLYDbn9C9et'  # Replace with your actual Thawani API key

def register(request):
    courses = Course.objects.all()
    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        civil_id = request.POST['civil_id']
        discount_code = request.POST.get('discount_code', '')
        gender = request.POST['gender']
        category = request.POST['category']
        course_id = request.POST['course']
        course = Course.objects.get(id=course_id)
        
        registration = CourseRegistration(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            civil_id=civil_id,
            discount_code=discount_code,
            gender=gender,
            category=category,
            course=course
        )
        registration.save()
        
       # Assuming `create_checkout_session` is defined elsewhere in your code
        session_id = create_checkout_session(registration)
        import os
        if session_id:
           # Establish connection to Thawani API endpoint
            conn = http.client.HTTPSConnection("uatcheckout.thawani.om")

            # Define request headers
            headers = {
                'Accept': "application/json",
                'thawani-api-key': "rRQ26GcsZzoEhbrP2HZvLYDbn9C9et"
            }

            # Send GET request to retrieve checkout session
            conn.request("GET", f"/api/v1/checkout/session/{session_id}", headers=headers)

            # Get response from the server
            res = conn.getresponse()

            # Read response data
            data = res.read().decode("utf-8")

            # Close connection
            conn.close()

            # Parse response data as JSON
            response_data = json.loads(data)
            print('----------------------------------------')
            print(response_data)
            # Check if the session retrieval was successful
            if response_data.get("success") and response_data.get("data"):
                payment_url = response_data["data"].get("success_url")
                print('----------------------------------------')
                print(payment_url)
                pkey = 'HGvTMLDssJghr9tlN9gr4DVYt0qyBy'
                if payment_url:
                    url = f"https://uatcheckout.thawani.om/pay/{session_id}?key={pkey}"

                    # Redirect the user to the payment URL
                    return redirect(url)
                else:
                    return render(request, 'cancel.html', {'message': 'Unable to process the payment at this time.'})
            else:
                    return render(request, 'cancel.html', {'message': 'Unable to process the payment at this time.'})
        else:
            # Log the error and render the cancellation page with an appropriate message
            return render(request, 'cancel.html', {'message': 'Unable to process the payment at this time.'})

    return render(request, 'courseRegistration.html', {'courses': courses})


def cancel(request):
    return render(request, 'cancel.html')
def done(request):
    return render(request, 'success.html')

import requests
import json
import http.client


def create_checkout_session(registration):
    url = "/api/v1/checkout/session"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'thawani-api-key': 'rRQ26GcsZzoEhbrP2HZvLYDbn9C9et'  # Replace with your actual Thawani API key
    }
    payload = {
        "client_reference_id": str(registration.id),
        "mode": "payment",
        "products": [
            {
                "name": registration.course.name,
                "quantity": 1,
                "unit_amount": int(registration.course.price * 100)  # Assuming price is in OMR, convert to Baisa
            }
        ],
        "success_url": 'http://127.0.0.1:7000/done',  # Replace with your actual success URL
        "cancel_url": 'http://127.0.0.1:7000/cancel',    # Replace with your actual cancel URL
        "metadata": {
            "Customer name": registration.full_name,
            "order id": registration.id
        }
    }

    # Convert payload to JSON string
    encoded_payload = json.dumps(payload)

    # Establish HTTPS connection
    conn = http.client.HTTPSConnection("uatcheckout.thawani.om")

    try:
        # Send POST request
        conn.request("POST", url, encoded_payload, headers)
        
        # Get response
        res = conn.getresponse()
        
        
        # Read response data
        data = res.read()
        
        # Decode response data
        decoded_data = data.decode("utf-8")
        
        # Print response data
        print(decoded_data)

        # Close connection
        conn.close()

        # Parse JSON data
        data = json.loads(decoded_data)

        # Access session_id
        session_id = data['data']['session_id']
        return session_id
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

