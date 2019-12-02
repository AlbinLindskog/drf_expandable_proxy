from .proxy import ExpandableProxy


class WritableNestedMixin:
    """
    ExpandableProxy is read only be default, just as standard nested serializers
    are, as there are too many different expected behaviors/use cases, most of them
    incompatible with each other, to support. This serializer mixin however covers
    the most common (my) use case by delegating to the expanded serializers create
    and update methods.
    """

    def create(self, validated_data):
        for field_name, field in self.fields.items():
            if not field.read_only and isinstance(field, ExpandableProxy) and field.expanded:

                validated_data[field_name] = self.fields[field_name].create(
                    validated_data=validated_data.pop(field_name)
                )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        for field_name, field in self.fields.items():
            if not field.read_only and isinstance(field, ExpandableProxy) and field.expanded:

                validated_data[field_name] = self.fields[field_name].update(
                    instance=getattr(instance, field_name),
                    validated_data=validated_data.pop(field_name)
                )
        return super().update(instance, validated_data)
