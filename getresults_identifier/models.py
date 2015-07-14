from django.db import models
from django.utils import timezone


class IdentifierHistory(models.Model):

    identifier = models.CharField(
        max_length=25,
    )

    identifier_type = models.CharField(
        max_length=25,
    )

    created_datetime = models.DateTimeField(
        default=timezone.now)

    class Meta:
        app_label = 'getresults_identifier'
