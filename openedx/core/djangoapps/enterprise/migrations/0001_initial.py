# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EnterpriseCustomer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Enterprise Customer name', max_length=500)),
                ('logo', models.ImageField(help_text='Please add only .PNG files for logo images.', max_length=255, null=True, upload_to=b'enterprise_logos', blank=True)),
                ('data_sharing_policy', models.CharField(help_text='Data sharing policy', max_length=20, choices=[(b'no_sharing', 'No data sharing requested'), (b'request', 'Request data sharing'), (b'require', 'Require data sharing')])),
                ('sso_providers', models.CharField(default=b'', help_text='Comma-separated list of Single Sign On providers slugs', max_length=500, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('members', models.ManyToManyField(help_text='Members of Enterprise Customer', related_name='enterprise_customer_membership', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Enterprise Customer',
            },
        ),
        migrations.CreateModel(
            name='EnterpriseCustomerHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(help_text='Enterprise Customer name', max_length=500)),
                ('logo', models.ImageField(help_text='Please add only .PNG files for logo images.', max_length=255, null=True, upload_to=b'enterprise_logos', blank=True)),
                ('data_sharing_policy', models.CharField(help_text='Data sharing policy', max_length=20, choices=[(b'no_sharing', 'No data sharing requested'), (b'request', 'Request data sharing'), (b'require', 'Require data sharing')])),
                ('sso_providers', models.CharField(default=b'', help_text='Comma-separated list of Single Sign On providers slugs', max_length=500, blank=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Enterprise Customer History',
            },
        ),
    ]
