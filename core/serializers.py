from rest_framework import serializers
from core.models import HedgeFund, Security, Filing, TickerMap


class HedgeFundSerializer(serializers.ModelSerializer):
    class Meta:
        model = HedgeFund
        fields = ['id', 'name', 'cik', 'strategy']


class SecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Security
        fields = ['name', 'ticker']


class FilingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filing
        fields = ['cusip', 'value', 'name_of_issuer', 'title_of_class', 'number_of_shares', 'investment_discretion',
                  'sh', 'voting_authority_sole', 'voting_authority_shared', 'voting_authority_none', 'report_date',
                  'hedge_fund', 'security']


class TickerMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = TickerMap
        fields = ['cusip', 'ticker']




