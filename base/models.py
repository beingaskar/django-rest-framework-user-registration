from django.db import models


class TimeStampedModel(models.Model):
    """
    An abstract model that provides fields required
    for most models such as creation time, updated time.

    """

    timestamp_created = models.DateTimeField(
        auto_now_add=True
    )

    timestamp_updated = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        abstract = True
