from django.shortcuts import render
from django.http import HttpResponse
from .models import Customer, Product, ProductInfo, Contract, Account, CustomerMemberAccount
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.core.serializers import serialize
import pandas as pd
import joblib
import os

CURRENT_WORKING_DIR = os.getcwd()
# Create your views here.
def index(_):
    return HttpResponse("Skibidi backend server up and running 🚀", 200)

def create_contract_account_member(request):
    """
    When user buys policy, they gotta provide 
    """
    # Assuming data is received via POST request
    received_data = json.loads(request.body)
    print(type(received_data['policy_id']))
    # Extract necessary fields from the received JSON
    policy_id = received_data.get('policy_id')
    ssn = received_data.get('ssn')
    credit_card_number = received_data.get('credit_card_number')
    # all_products = Product.objects.all()
    print("policy_id is ", policy_id, type(policy_id))
    # for product in all_products:
    #     print(f"Policy ID: {type(product.policy_id)}, Line of Business: {product.line_of_business}, Plan Name: {product.plan_name}")
    # Retrieve product details based on the policy ID
    product = Product.objects.get(policy_id=policy_id)
    product_info = ProductInfo.objects.get(product_id = policy_id)

    # Parse duration string to calculate expiration date
    duration_str = product_info.duration
    duration_split = duration_str.split()
    duration_value = int(duration_split[0])
    duration_unit = duration_split[1].lower()

    # Calculate expiration date based on duration
    expiration_date = datetime.datetime.now()
    if 'year' in duration_unit:
        expiration_date += datetime.timedelta(days=duration_value * 365)
    elif 'month' in duration_unit:
        expiration_date += datetime.timedelta(days=duration_value * 30)
    elif 'day' in duration_unit:
        expiration_date += datetime.timedelta(days=duration_value)
    else:
        pass  # Handle other cases or default to a specific duration

    # Create a Contract record
    contract = Contract.objects.create(
        coverage_type=product.line_of_business,
        activity_status='Active',
        card_type='Credit',
        expiration_date=expiration_date,
        credit_card_no=credit_card_number,
        duration=duration_str
    )

    # Retrieve the customer based on the received SSN
    customer = Customer.objects.get(CustSSN=ssn)

    # Create an Account record associated with the contract
    account = Account.objects.create(
        cust_ssn=customer,
        contract_number=contract,
        start_date=datetime.datetime.now()
    )

    # Create a CustomerMemberAccount record linking Account and Customer
    customer_member_account = CustomerMemberAccount.objects.create(
        account_name=account,
        cust_ssn=customer,
        type=product
    )

    return JsonResponse({'success': 'Records created successfully'}, status=201)

@csrf_exempt
def add_user(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)  # Get JSON data from request.body

            # Assuming JSON data is in the format:
            # {'CustSSN': '123456789', 'CustFirstName': 'John', ...}
            # Process and save the customer information
            Customer.objects.create(**json_data)
            # predict using model, what obesity type the customer is 
            # if user is obese, then check for policy on obesity andn heart disease
            # check number of obese customers
            # if more than a threshold, update pricing to give discount (affordable insurance)
            return JsonResponse({'message': 'Customer data saved successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data received'}, status=400)

    return JsonResponse({'message': 'Only POST requests are allowed'}, status=405)

@csrf_exempt
def get_policies(request):
    """
    Retrieve all products along with their descriptions
    """
    all_products_with_descriptions = Product.objects.select_related('productinfo').values(
        'policy_id', 'line_of_business', 'plan_name',
        'productinfo__product_description', 'productinfo__premium_amount', 'productinfo__duration',
        # Include all fields from both models as needed
    )

    return JsonResponse(list(all_products_with_descriptions), safe=False)


@csrf_exempt
def add_policies(request):
    
    # Get the product you want to delete
    product_to_delete = Product.objects.get(policy_id='001')

    # Delete the product
    product_to_delete.delete()
    # Create five products with descriptions
    
    # Create five products with product information
    product_data = [
        {
            "policy_id": "006",
            "line_of_business": "mental",
            "plan_name": "Mental Health Assistance Coverage Advanced",
            "description": "Support for mental health with counseling and therapy. Also includes 24/7 virtual care",
            "premium_amount": 350.00,
            "duration": "2 years"
        }
    ]

    # Loop through the product data and create Product and ProductInfo instances
    for data in product_data:
        # Create Product instance
        product = Product.objects.create(
            policy_id=data['policy_id'],
            line_of_business=data['line_of_business'],
            plan_name=data['plan_name'],
        )
        
        # Create ProductInfo instance associated with the Product
        ProductInfo.objects.create(
            product_id=product,
            product_description=data['description'],
            premium_amount=data['premium_amount'],
            duratioon = data['duration']
        )

    return HttpResponse("Backend server up and running")

#def process_claims():
@csrf_exempt
def predict_obesity_levels(request):
    """
    Get user's personal data from frontend and predict the obesity levels
    Use these obesity predictions to adjust pricing for insurance policies for those in need
    """
    # Get data as JSON
    if request.method == 'GET':
        json_data = json.loads(request.body)

        try:
            single_user_row = pd.DataFrame([json_data])
        except Exception as e:
            print(f"{e} - can't read JSON")
        # load pipeline
        labels_from_file = {}
        
        with open(f"{CURRENT_WORKING_DIR}/backend/ml/class_labels.json", "r") as infile: 
                labels_from_file = json.load(infile)
        
        pipeline_loaded = joblib.load(f'{CURRENT_WORKING_DIR}/backend/ml/model_file.joblib')
        prediction_for_user = pipeline_loaded.predict(single_user_row.iloc[[0]])[0]
        obesity_level = labels_from_file[str(prediction_for_user)]

        ## Find out how many users have weight insurance needs
        ## Change pricing accordingly
        product_info = ProductInfo.objects.get(product_id=Product.objects.get(line_of_business='weight').policy_id)
        print(product_info.product_id)
        
        
        # Update the price attribute of the ProductInfo instance
        product_info.premium_amount = 200.0  # Replace with the new price value
        # Save the changes to the database
        product_info.save()

        return HttpResponse({f"User is {obesity_level}"}, status=201)
        
    else:
        return HttpResponse("Wrong method", status = 405)