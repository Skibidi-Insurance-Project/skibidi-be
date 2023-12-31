# Generated by Django 5.0 on 2023-12-15 05:33

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Companies",
            fields=[
                (
                    "company_code",
                    models.CharField(max_length=100, primary_key=True, serialize=False),
                ),
                ("company_name", models.CharField(max_length=255)),
                ("legacy_company_no", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Contract",
            fields=[
                (
                    "contract_number",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("coverage_type", models.CharField(max_length=100)),
                ("activity_status", models.CharField(max_length=100)),
                ("card_type", models.CharField(max_length=100)),
                ("expiration_date", models.DateField()),
                ("credit_card_no", models.CharField(max_length=100)),
                ("duration", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Customer",
            fields=[
                (
                    "CustSSN",
                    models.CharField(max_length=11, primary_key=True, serialize=False),
                ),
                ("CustFirstName", models.CharField(max_length=255)),
                ("CustLastName", models.CharField(max_length=255)),
                ("CustDOB", models.DateField()),
                (
                    "Gender",
                    models.CharField(
                        choices=[("M", "Male"), ("F", "Female"), ("O", "Other")],
                        max_length=1,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "policy_id",
                    models.CharField(max_length=100, primary_key=True, serialize=False),
                ),
                (
                    "line_of_business",
                    models.CharField(
                        choices=[
                            ("eye", "Eye"),
                            ("dental", "Dental"),
                            ("heart", "Heart"),
                            ("weight", "Weight"),
                            ("mental", "Mental"),
                        ],
                        max_length=20,
                    ),
                ),
                ("plan_name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Address",
            fields=[
                (
                    "house",
                    models.CharField(max_length=100, primary_key=True, serialize=False),
                ),
                ("city", models.CharField(max_length=100)),
                ("state", models.CharField(max_length=100)),
                (
                    "cust_ssn",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend.customer",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Account",
            fields=[
                (
                    "account_name",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("start_date", models.DateField()),
                (
                    "contract_number",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="backend.contract",
                    ),
                ),
                (
                    "cust_ssn",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="backend.customer",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CustomerClaimsContract",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "contract_number",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend.contract",
                    ),
                ),
                (
                    "cust_ssn",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend.customer",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CustomerAccount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "account_name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend.account",
                    ),
                ),
                (
                    "cust_ssn",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend.customer",
                    ),
                ),
                (
                    "type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductInfo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("product_description", models.TextField()),
                (
                    "premium_amount",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "product_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ContractProduct",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("line_of_business", models.CharField(max_length=20)),
                (
                    "contract",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend.contract",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend.product",
                    ),
                ),
            ],
            options={
                "unique_together": {("contract", "product")},
            },
        ),
    ]
