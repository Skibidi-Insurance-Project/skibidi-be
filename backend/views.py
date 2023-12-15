from django.shortcuts import render
from django.http import HttpResponse
from .models import Customer, Product, ProductInfo, Contract, Account, CustomerMemberAccount
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.core.serializers import serialize

# Create your views here.
def index(_):
    return HttpResponse("Skibidi backend server up and running 🚀")

def create_contract_account_member(request):
    """
    When user buys policy, they gotta provide 
    """
    # Assuming data is received via POST request
    received_data = request.POST
    
    # Extract necessary fields from the received JSON
    policy_id = received_data.get('policy_id')
    ssn = received_data.get('ssn')
    credit_card_number = received_data.get('credit_card_number')

    # Retrieve product details based on the policy ID
    product = Product.objects.get(policy_id=policy_id)
    product_info = Product.objects.get(policy_id=product)

    # Parse duration string to calculate expiration date
    duration_str = product_info.duration
    duration_split = duration_str.split()
    duration_value = int(duration_split[0])
    duration_unit = duration_split[1].lower()

    # Calculate expiration date based on duration
    expiration_date = datetime.now()
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
        coverage_type=product.coverage_type,
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
        account_name=f"Account for {customer.CustSSN}",
        contract_number=contract,
        start_date=datetime.now()
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
