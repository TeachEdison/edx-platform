# -*- coding: utf-8 -*-
"""
Models for Enterprise features
"""
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel


class EnterpriseCustomerManager(models.Manager):
    """
    Model manager for Enterprise Customer model.

    Filters out inactive Enterprise Customers, otherwise works the same as default model manager.
    """
    # This manager filters out some records, hence according to the Django docs it must not be used
    # for related field access. Although False is default value, it still makes sense to set it explicitly
    # https://docs.djangoproject.com/en/1.10/topics/db/managers/#base-managers
    use_for_related_fields = False

    def get_queryset(self):
        """
        Returns a new QuerySet object. Filters out inactive Enterprise Customers
        """
        return super(EnterpriseCustomerManager, self).get_queryset().filter(active=True)


class EnterpriseCustomer(models.Model):
    """
    Enterprise Customer is an organization or a group of people that "consumes" courses: members of Enterprise
    Customer take courses on the edX platform.

    Enterprise Customer might be providing certain benefits to their members, like discounts to paid course
    enrollments, and also might request (or require) sharing learner results with them.

    Fields:
        [implicit] id (IntegerField): EnterpriseCustomer identifier, PRIMARY KEY
        name (CharField): Enterprise Customer name
        logo (ImageField):  Enterprise Customer logo
        data_sharing_policy (CharField): stores data sharing policy: either no data sharing,
                                         requested data sharing (learners are allowed to opt-in) or required data
                                         sharing (learners must share their data)
        sso_providers (CharField): list of comma-separated SSO provider slugs. Providers in this list should link
                                    users registered with that provider with Enterprise Customer
        active (BooleanField): used to mark inactive Enterprise Customers - implements "soft delete" pattern
        members (ManyToMany[User]): list of Enterprise Customer members.
    """
    NO_DATA_SHARING = "no_sharing"
    REQUEST_DATA_SHARING = "request"
    REQUIRE_DATA_SHARING = "require"

    class Meta(object):
        """
        Meta class for EnterpriseCustomer model
        """
        app_label = "enterprise"
        verbose_name = "Enterprise Customer"

    objects = EnterpriseCustomerManager()
    all_objects = models.Manager()

    name = models.CharField(max_length=500, blank=False, null=False, help_text=_(u"Enterprise Customer name."))
    logo = models.ImageField(
        upload_to="enterprise_logos",
        help_text=_(u"Please add only .PNG files for logo images."),
        null=True, blank=True, max_length=255
    )
    data_sharing_policy = models.CharField(
        blank=False, null=False, help_text=_(u"Data sharing policy"), max_length=20,
        choices=(
            (NO_DATA_SHARING, _(u"No data sharing requested")),
            (REQUEST_DATA_SHARING, _(u"Request data sharing")),
            (REQUIRE_DATA_SHARING, _(u"Require data sharing")),
        )
    )
    sso_providers = models.CharField(
        blank=True, null=False, default="", max_length=500,
        help_text=_(u"Comma-separated list of Single Sign On providers slugs.")
    )
    active = models.BooleanField(default=True)
    # at a glance it seemed to be beneficial to use EnterpriseCustomerManager as related field manager here, so that
    # only active enterprise customers are shown on the User side of relationship. However, Django docs explicitly
    # mentions that it must not be done - see comment on EnterpriseCustomerManager
    members = models.ManyToManyField(
        User, related_name="enterprise_customer_membership", blank=True,
        help_text=_(u"Members of Enterprise Customer.")
    )

    @property
    def sso_providers_list(self):
        """
        List of SSO provider slugs
        """
        return [provider_slug.strip() for provider_slug in self.sso_providers.split(",")]

    def __unicode__(self):
        return u"<EnterpriseCustomer: {name}>".format(name=self.name)

    def __repr__(self):
        return self.__unicode__()


class EnterpriseCustomerHistory(TimeStampedModel):
    """
    This is an archive table for EnterpriseCustomer, so that we can maintain a history of
    changes. Note that `members` field is omitted to avoid storing huge amounts of user affinity data.-

    Fields:
        id (IntegerField): Enterprise Customer identified
        name (CharField): Enterprise Customer name
        logo (ImageField):  Enterprise Customer logo
        data_sharing_policy (CharField): stores data sharing policy: either no data sharing,
                                         requested data sharing (learners are allowed to opt-in) or required data
                                         sharing (learners must share their data)
        sso_providers (CharField): list of comma-separated SSO provider slugs. Providers in this list should link
                                    users registered with that provider with Enterprise Customer
        active (BooleanField): used to mark inactive Enterprise Customers - implements "soft delete" pattern
    """
    class Meta(object):
        """
        Meta class for EnterpriseCustomerHistory model
        """
        app_label = "enterprise"
        verbose_name = "Enterprise Customer History"

    name = models.CharField(max_length=500, blank=False, null=False, help_text=_(u"Enterprise Customer name."))
    logo = models.ImageField(
        upload_to='enterprise_logos',
        help_text=_(u'Please add only .PNG files for logo images.'),
        null=True, blank=True, max_length=255
    )
    data_sharing_policy = models.CharField(
        blank=False, null=False, help_text=_(u"Data sharing policy"), max_length=20,
        choices=(
            (EnterpriseCustomer.NO_DATA_SHARING, _(u"No data sharing requested")),
            (EnterpriseCustomer.REQUEST_DATA_SHARING, _(u"Request data sharing")),
            (EnterpriseCustomer.REQUIRE_DATA_SHARING, _(u"Require data sharing")),
        )
    )
    sso_providers = models.CharField(
        blank=True, null=False, default="", max_length=500,
        help_text=_(u"Comma-separated list of Single Sign On providers slugs.")
    )
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return u"<EnterpriseCustomer: {name}, Last Modified: {modified} >".format(
            modified=self.modified,
            name=self.name,
        )

    def __repr__(self):
        return self.__unicode__()


@receiver(post_save, sender=EnterpriseCustomer)
def update_enterprise_customer_history(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """
    Add enterprise customer changes to enterprise customer history.

    Args:
        sender: sender of the signal i.e. EnterpriseCustomer model
        instance: EnterpriseCustomer instance associated with the current signal
        **kwargs: extra key word arguments
    """
    EnterpriseCustomerHistory.objects.create(
        name=instance.name,
        logo=instance.logo,
        data_sharing_policy=instance.data_sharing_policy,
        sso_providers=instance.sso_providers,
        active=instance.active,
    )
