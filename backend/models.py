from django.db import models
import uuid

# Create your models here.
class Customer(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    CustSSN = models.CharField(max_length=11, primary_key=True)
    CustFirstName = models.CharField(max_length=255)
    CustLastName = models.CharField(max_length=255)
    CustDOB = models.DateField()
    Gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

class Contract(models.Model):
    contract_number = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coverage_type = models.CharField(max_length=100)
    activity_status = models.CharField(max_length=100)
    card_type = models.CharField(max_length=100)
    expiration_date = models.DateField()
    credit_card_no = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)

class Account(models.Model):
    cust_ssn = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    account_name = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract_number = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()

class Companies(models.Model):
    company_code = models.CharField(primary_key=True, max_length=100)
    company_name = models.CharField(max_length=255)
    legacy_company_no = models.CharField(max_length=100)

class CustomerClaimsContract(models.Model):
    cust_ssn = models.ForeignKey(Customer, on_delete=models.CASCADE)
    contract_number = models.ForeignKey(Contract, on_delete=models.CASCADE)


class Product(models.Model):
    LINE_OF_BUSINESS_CHOICES = [
        ('eye', 'Eye'),
        ('dental', 'Dental'),
        ('heart', 'Heart'),
        ('weight', 'Weight'),
        ('mental', 'Mental'),
    ]

    policy_id = models.CharField(primary_key=True, max_length=100)
    line_of_business = models.CharField(max_length=20, choices=LINE_OF_BUSINESS_CHOICES)
    plan_name = models.CharField(max_length=255)

class ProductInfo(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    product_description = models.TextField()
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=100, default="2 years")

class ContractProduct(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    line_of_business = models.CharField(max_length=20)  # Additional attribute

    class Meta:
        unique_together = ('contract', 'product')

class Address(models.Model):
    house = models.CharField(primary_key=True, max_length=100)
    cust_ssn = models.ForeignKey(Customer, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

class CustomerMemberAccount(models.Model):
    account_name = models.ForeignKey(Account, on_delete=models.CASCADE)
    cust_ssn = models.ForeignKey(Customer, on_delete=models.CASCADE)
    type = models.ForeignKey(Product, on_delete=models.CASCADE)  # Additional attribute 'Type'
