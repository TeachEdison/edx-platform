# -*- coding: utf-8 -*-
"""
Django admin integration for enterprise app
"""
from django.contrib import admin
from django.http import HttpResponse
import unicodecsv

from openedx.core.djangoapps.enterprise.models import EnterpriseCustomer, EnterpriseCustomerHistory


def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    # adapted from https://gist.github.com/mgerring/3645889
    def export_as_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta

        if not fields:
            field_names = [field.name for field in opts.fields]
        else:
            field_names = fields

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={filename}.csv'.format(
            filename=unicode(opts).replace('.', '_')
        )

        writer = unicodecsv.writer(response, encoding='utf-8')
        if header:
            writer.writerow(field_names)
        for obj in queryset:
            row = []
            for field_name in field_names:
                field = getattr(obj, field_name)
                if callable(field):
                    value = field()
                else:
                    value = field
                if value:
                    row.append(value)
                elif value is None:
                    row.append("[Not Set]")
                else:
                    row.append("[Empty]")
            writer.writerow(row)
        return response

    export_as_csv.short_description = description
    return export_as_csv


@admin.register(EnterpriseCustomer)
class EnterpriseCustomerAdmin(admin.ModelAdmin):
    """
    Django admin model for EnterpriseCustomer
    """
    list_display = ('name', 'active', 'data_sharing_policy', 'sso_providers', 'logo')
    search_fields = ('name', 'data_sharing_policy', 'sso_providers')
    filter_horizontal = ('members', )

    actions = [
        export_as_csv_action("CSV Export", fields=['name', 'active', 'data_sharing_policy', 'sso_providers', 'logo'])
    ]

    class Meta(object):
        """
        Meta class for EnterpriseCustomer admin model
        """
        model = EnterpriseCustomer


@admin.register(EnterpriseCustomerHistory)
class EnterpriseCustomerHistoryAdmin(admin.ModelAdmin):
    """
    Django admin model for EnterpriseCustomerHistory
    """
    list_display = ('name', 'active', 'data_sharing_policy', 'sso_providers', 'logo', 'created', 'modified')
    search_fields = ('name', 'data_sharing_policy', 'sso_providers', 'created', 'modified')
    exclude = ('members',)

    ordering = ['-created']

    class Meta(object):
        """
        Meta class for EnterpriseCustomerHistory admin model
        """
        model = EnterpriseCustomerHistory

    def has_add_permission(self, request):
        """Don't allow adds"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Don't allow deletes"""
        return False
