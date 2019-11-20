from rest_framework import serializers

from drf_expandable_proxy import ExpandableProxy, WritableNestedMixin

from .models import Flavor, Scoop, IceCream, Order


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('id', 'paid')


class IceCreamSerializer(WritableNestedMixin, serializers.ModelSerializer):
    order = ExpandableProxy(
        serializer=OrderSerializer(),
        field=serializers.PrimaryKeyRelatedField(queryset=Order.objects.all()),
    )

    class Meta:
        model = IceCream
        fields = ('id', 'order', 'with_waffle',)


class FlavorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flavor
        fields = ('id', 'flavor', )


class ScoopSerializer(WritableNestedMixin, serializers.ModelSerializer):

    flavor = ExpandableProxy(
        serializer=FlavorSerializer(),
        field=serializers.PrimaryKeyRelatedField(queryset=Flavor.objects.all()),
    )
    ice_cream = ExpandableProxy(
        serializer=IceCreamSerializer(),
        field=serializers.PrimaryKeyRelatedField(queryset=IceCream.objects.all()),
    )

    class Meta:
        model = Scoop
        fields = ('id', 'size', 'flavor', 'ice_cream')
