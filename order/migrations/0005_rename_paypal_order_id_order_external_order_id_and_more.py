# Generated by Django 5.1.1 on 2024-09-20 09:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_order_approval_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='paypal_order_id',
            new_name='external_order_id',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='approval_url',
            new_name='payment_url',
        ),
    ]
