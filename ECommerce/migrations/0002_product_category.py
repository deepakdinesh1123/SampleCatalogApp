# Generated by Django 4.2.11 on 2024-06-03 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_models', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.CharField(blank=True, choices=[('electronics', 'Electronics'), ('fashion', 'Fashion'), ('home', 'Home')], max_length=100, null=True),
        ),
    ]
