from django.utils.functional import cached_property

from rest_framework.serializers import Field, ListSerializer


class ExpandableProxy(Field):
    """
    A mixin allowing fields to be expandable.

    Expands the data through the passed serializer if query_param is set to the
    field name, otherwise it passes the data to the field.
    """
    query_param = 'expand'

    def __init__(self, serializer, field):
        self._serializer = serializer
        self._field = field
        self.proxied = None
        super().__init__(self)

    def __getattribute__(self, name):
        """
        ExtandableProxy needs to inherit from Field, so it's auto registered by
        the serializer metaclass. However, we don't want it to inherit the
        methods or attributes from Field, we want it to proxy the methods of
        the underlying field/serializer, so we override __getattribute__.
        """
        if object.__getattribute__(self, 'proxied') and name not in ['proxied', 'expanded', 'level']:
            return getattr(object.__getattribute__(self, 'proxied'), name)
        else:
            return object.__getattribute__(self, name)

    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        self.proxied = [self._field, self._serializer][self.expanded]
        self.proxied.bind(field_name, parent)

    @cached_property
    def expanded(self):
        if not 'request' in self.context:
            return False

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
