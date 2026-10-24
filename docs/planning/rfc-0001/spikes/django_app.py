"""Django spike: one view, the ORM, a Django template. Run with gunicorn."""

import os
from pathlib import Path

import django
from django.conf import settings

HERE = Path(__file__).parent
settings.configure(
    DEBUG=False,
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=["*"],
    INSTALLED_APPS=["django.contrib.contenttypes"],
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "spike",
            "USER": "spike",
            "PASSWORD": "spike",
            "HOST": "127.0.0.1",
            "PORT": os.environ.get("PGPORT", "5433"),
            "CONN_MAX_AGE": None,  # keep connections, as a production setting would
        }
    },
    TEMPLATES=[{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [HERE]}],
)
django.setup()

from django.db import models  # noqa: E402
from django.shortcuts import render  # noqa: E402
from django.urls import path  # noqa: E402
from money import summary  # noqa: E402


class Quote(models.Model):
    symbol = models.TextField(primary_key=True)
    price = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        app_label = "spike"
        db_table = "quote"
        managed = False


class Account(models.Model):
    user_id = models.TextField(primary_key=True)
    balance = models.DecimalField(max_digits=14, decimal_places=2)
    open_balance = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        app_label = "spike"
        db_table = "account"
        managed = False


class Holding(models.Model):
    account = models.ForeignKey(Account, models.DO_NOTHING, db_column="user_id")
    quote = models.ForeignKey(Quote, models.DO_NOTHING, db_column="symbol")
    quantity = models.DecimalField(max_digits=14, decimal_places=4)

    class Meta:
        app_label = "spike"
        db_table = "holding"
        managed = False


def home(request, user_id):
    account = Account.objects.get(pk=user_id)
    rows = [
        (h.quote_id, h.quantity, h.quote.price)
        for h in Holding.objects.filter(account=account).select_related("quote")
    ]
    context = {"user_id": user_id, **summary(account.balance, account.open_balance, rows)}
    return render(request, "home.html", context)


urlpatterns = [path("home/<str:user_id>", home)]

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
