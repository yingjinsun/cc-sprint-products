# Generated by Django 3.2.5 on 2021-10-12 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='amount',
            field=models.IntegerField(default=0),
        ),
    ]
