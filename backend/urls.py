from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add_customer", views.add_user, name="add_user"),
    path("add_policy", views.add_policies, name="add_policies"),
    path("purchase_policy", views.create_contract_account_member, name="create_account"),
    #path("create_claim")
    path("get_policies", views.get_policies, name="retreive_policies")
]