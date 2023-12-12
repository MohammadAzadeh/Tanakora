# Generated by Django 4.1.1 on 2022-09-22 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_remove_cartitem_user_cartitem_product_descp_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='product_descp',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='product_name',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='product_price',
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='product_quantity',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]