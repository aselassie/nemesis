from rest_framework import routers
from core.views import HedgeFundViewSet, SecurityViewSet, FilingViewSet, TickerMapViewSet, ResearchViewSet


router = routers.DefaultRouter()

router.register('hedge-fund', HedgeFundViewSet)
router.register('security', SecurityViewSet)
router.register('filing', FilingViewSet)
router.register('ticker-map', TickerMapViewSet)
router.register('research', ResearchViewSet, basename='research')

urlpatterns = router.urls
