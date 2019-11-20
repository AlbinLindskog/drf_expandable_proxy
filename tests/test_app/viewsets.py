from rest_framework import viewsets

from .models import Flavor, Scoop, IceCream
from .serializers import FlavorSerializer, ScoopSerializer, IceCreamSerializer


class FlavorViewSet(viewsets.ModelViewSet):

    serializer_class = FlavorSerializer
    queryset = Flavor.objects.all()


class ScoopViewSet(viewsets.ModelViewSet):

    serializer_class = ScoopSerializer
    queryset = Scoop.objects.all()


class IceCreamViewset(viewsets.ModelViewSet):

    serializer_class = IceCreamSerializer
    queryset = IceCream.objects.all()