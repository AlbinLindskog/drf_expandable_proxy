from django.utils.functional import cached_property

from rest_framework.serializers import BaseSerializer, ListSerializer


class ExpandableProxyMetaClass(type):
    """
    ExtandableProxy needs to inherit from Field, so it's autoregistered by the
    serializer metaclass. However, we don't want it to inherit the methods from
    Field, we want it to proxy the methods of the underlying field/serializer,
    so we use this meta class to rebind the methods.
    """
    proxied_methods = ['to_internal_value', 'to_representation', 'update', 'create']

    @staticmethod
    def lazy_ref(method_name):
        """
        Create a lazy reference to the method method_name on
        ExpandableProxy.proxied since proxied isn't set at declaration,
        and thus isn't available to the metaclass, but be comes available when
        ExpandableProxy.bind is called.

        Note: wrapper does not wrap attributes of the method, like __name__ or
        __doc__, because I can't be bothered to write a lazy version of
        functools.wraps.
        """
        def wrapper(self, *args, **kwargs):
            return getattr(self.proxied, method_name)(*args, **kwargs)
        return wrapper

    def __new__(cls, name, bases, attrs):
        new_cls = super(ExpandableProxyMetaClass, cls).__new__(cls, name, bases, attrs)
        for method_name in cls.proxied_methods:
            setattr(new_cls, method_name, cls.lazy_ref(method_name))
        return new_cls


class ExpandableProxy(BaseSerializer, metaclass=ExpandableProxyMetaClass):
    """
    A mixin allowing fields to be expandable.

    Expands the data through the passed serializer if query_param is set to the
    field name, otherwise it passes the data to the field.
    """
    query_param = 'expand'

    def __init__(self, serializer, field, *args, **kwargs):
        self._serializer = serializer
        self._field = field
        self.proxied = None
        super().__init__(*args, **kwargs)

    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        self.proxied = [self._field, self._serializer][self.expanded]
        self.proxied.bind(field_name, parent)

    @cached_property
    def expanded(self):
        query_params = self.context['request'].query_params.getlist(self.query_param)
        split_params = [param.split('.') for param in query_params]
        level_params = [param[self.level] for param in split_params if len(param) > self.level]
        return self.field_name in level_params

    @cached_property
    def level(self):
        root, level = self, -1  # ExpandableProxy can never be the root, hence -1
        while root.parent is not None:
            root = root.parent

            # When passing many=True to a serializer DRF non-transparently
            # adds a ListSerializer to the parent chain. If we do not account
            # for this ExpandableProxy would behave differently for list and
            # retrieve calls.
            if not isinstance(root, ListSerializer):
                level = level + 1
        return level
