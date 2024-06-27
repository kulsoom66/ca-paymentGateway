# Import necessary modules and models
from django.shortcuts import render, redirect
from .models import Course, CourseRegistration
from django.conf import settings
import json
import http.client
import os

# Thawani API key (replace with your actual key)
THAWANI_API_KEY = 'rRQ26GcsZzoEhbrP2HZvLYDbn9C9et'

# View for course registration
def register(request):
    # Retrieve all courses from the database
    courses = Course.objects.all()
    
    # Check if the request method is POST
    if request.method == 'POST':
        # Get form data from the POST request
        full_name = request.POST['full_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        civil_id = request.POST['civil_id']
        discount_code = request.POST.get('discount_code', '')
        gender = request.POST['gender']
        category = request.POST['category']
        course_id = request.POST['course']
        
        # Get the selected course from the database
        course = Course.objects.get(id=course_id)
        
        # Create a new course registration instance
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
        # Save the registration to the database
        registration.save()
        
        # Create a checkout session for the registration
        session_id = create_checkout_session(registration)
        
        # If the session is successfully created
        if session_id:
            # Establish connection to Thawani API endpoint
            conn = http.client.HTTPSConnection("uatcheckout.thawani.om")
            
            # Define request headers
            headers = {
                'Accept': "application/json",
                'thawani-api-key': THAWANI_API_KEY
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
            
            # Check if the session retrieval was successful
            if response_data.get("success") and response_data.get("data"):
                payment_url = response_data["data"].get("success_url")
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
    
    # Render the course registration page with available courses
    return render(request, 'courseRegistration.html', {'courses': courses})

# View for the cancellation page
def cancel(request):
    return render(request, 'cancel.html')

# View for the success page
def succeed(request):
    return render(request, 'success.html')

# Function to create a checkout session
def create_checkout_session(registration):
    url = "/api/v1/checkout/session"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'thawani-api-key': THAWANI_API_KEY  # Replace with your actual Thawani API key
    }
    payload = {
        "client_reference_id": str(registration.id),
        "mode": "payment",
        "products": [
            {
                "name": registration.course.name,
                "quantity": 1,
                "unit_amount": int(registration.course.price * 1000)  # Assuming price is in OMR, convert to Baisa
            }
        ],
        "success_url": 'http://127.0.0.1:7000/succeed',  # Replace with your actual success URL
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
