# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('enterprise', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enterprisecustomer',
            name='members',
            field=models.ManyToManyField(help_text='Members of Enterprise Customer.', related_name='enterprise_customer_membership', null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='enterprisecustomer',
            name='name',
            field=models.CharField(help_text='Enterprise Customer name.', max_length=500),
        ),
        migrations.AlterField(
            model_name='enterprisecustomer',
            name='sso_providers',
            field=models.CharField(default=b'', help_text='Comma-separated list of Single Sign On providers slugs.', max_length=500, blank=True),
        ),
        migrations.AlterField(
            model_name='enterprisecustomerhistory',
            name='name',
            field=models.CharField(help_text='Enterprise Customer name.', max_length=500),
        ),
        migrations.AlterField(
            model_name='enterprisecustomerhistory',
            name='sso_providers',
            field=models.CharField(default=b'', help_text='Comma-separated list of Single Sign On providers slugs.', max_length=500, blank=True),
        ),
    ]
