from rest_framework import viewsets
from core.serializers import HedgeFundSerializer, SecuritySerializer, FilingSerializer, TickerMapSerializer
from core.models import HedgeFund, Security, Filing, TickerMap
from rest_framework.response import Response
import pandas as pd
import numpy as np


class HedgeFundViewSet(viewsets.ModelViewSet):
    serializer_class = HedgeFundSerializer
    queryset = HedgeFund.objects.all()


class SecurityViewSet(viewsets.ModelViewSet):
    serializer_class = SecuritySerializer
    queryset = Security.objects.all()


class FilingViewSet(viewsets.ModelViewSet):
    serializer_class = FilingSerializer
    queryset = Filing.objects.all()


class TickerMapViewSet(viewsets.ModelViewSet):
    serializer_class = TickerMapSerializer
    queryset = TickerMap.objects.all()


class ResearchViewSet(viewsets.GenericViewSet):

    def list(self, request):
        some_data = np.random.rand(100)
        other_data = np.random.rand(100)
        dates = pd.date_range(start="2010-01-01", periods=100, freq="M")
        df = pd.DataFrame({"Fund A": some_data, 'Fund B': other_data}, index=dates)
        serialized = df.reset_index().to_dict(orient='records')
        return Response(serialized)

