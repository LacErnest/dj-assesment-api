from rest_framework import serializers
from .models import MenuItem

class MenuItemSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'parent', 'depth', 'created_at', 'updated_at']
        read_only_fields = ['depth', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['parent'] = instance.parent.name if instance.parent else None
        return representation

    def validate_name(self, value):
        instance = getattr(self, 'instance', None)
        if MenuItem.objects.filter(name=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("A menu item with this name already exists.")
        return value
