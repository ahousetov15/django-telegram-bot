import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from dtb.settings import MSK_TZ


nb = dict(null=True, blank=True)


class CreateTracker(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name="Создан"
    )

    class Meta:
        abstract = True
        ordering = ("created_at",)


class CreateUpdateTracker(CreateTracker):
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta(CreateTracker.Meta):
        abstract = True


class GetOrNoneManager(models.Manager):
    """returns none if object doesn't exist else model instance"""

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return None


def datetime_str(dt_obj: datetime) -> str:
    if dt_obj:
        dt_obj = dt_obj.astimezone(MSK_TZ).strftime("%Y-%m-%d %H-%M-%S")
    else:
        dt_obj = (
            datetime.datetime.now().astimezone(MSK_TZ).strftime("%Y-%m-%d %H-%M-%S")
        )
    return dt_obj


def datetime_by_msk(dt_obj: datetime) -> datetime:
    if dt_obj:
        dt_obj = dt_obj.astimezone(MSK_TZ)
    else:
        dt_obj = datetime.datetime.now().astimezone(MSK_TZ)
    return dt_obj
