from rest_framework import routers
from .viewsets import FlavorViewSet, ScoopViewSet, IceCreamViewset


router = routers.DefaultRouter()


router.register(r'flavors', FlavorViewSet)
router.register(r'scoops', ScoopViewSet)
router.register(r'icecream', IceCreamViewset)
