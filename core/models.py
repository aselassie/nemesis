from django.db import models


# Create your models here.
class HedgeFund(models.Model):
    name = models.TextField()
    cik = models.TextField()
    address = models.TextField(null=True, blank=True)
    strategy = models.TextField()

    def __str__(self):
        return self.name


class Security(models.Model):
    name = models.TextField()
    ticker = models.TextField()


class Filing(models.Model):
    cusip = models.TextField()
    value = models.IntegerField()
    name_of_issuer = models.TextField()
    title_of_class = models.TextField()
    number_of_shares = models.IntegerField()
    investment_discretion = models.TextField()
    sh = models.TextField()
    voting_authority_sole = models.IntegerField()
    voting_authority_shared = models.IntegerField()
    voting_authority_none = models.IntegerField()
    report_date = models.DateField()
    hedge_fund = models.ForeignKey(HedgeFund, on_delete=models.PROTECT)
    security = models.ForeignKey(Security, on_delete=models.PROTECT)


class TickerMap(models.Model):
    cusip = models.TextField()
    ticker = models.TextField()
    as_of_date = models.DateField(null=True)
