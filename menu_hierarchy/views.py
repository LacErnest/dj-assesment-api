from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import MenuItem
from .serializers import MenuItemSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class MenuItemViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing `MenuItem` objects. Provides CRUD operations and hierarchical structure handling.

    Actions:
        - `retrieve`: Get details of a specific `MenuItem`, including its depth and root item.
        - `create`: Create a new `MenuItem`, with depth calculated based on its parent item.
        - `list`: List all `MenuItem` objects with hierarchical structure.
        - `destroy`: Delete a specific `MenuItem`, ensuring it does not have any children.
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_menu_item_schema():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'parent': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                'depth': openapi.Schema(type=openapi.TYPE_INTEGER),
                'created_at': openapi.Schema(type=openapi.FORMAT_DATETIME),
                'updated_at': openapi.Schema(type=openapi.FORMAT_DATETIME),
            }
        )

    @swagger_auto_schema(
        responses={200: openapi.Response('Success', MenuItemSerializer)},
        operation_description="Retrieve a specific `MenuItem` instance and include its depth and root item in the response."
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'data': serializer.data,
            'depth': instance.depth,
            'root_item': self.get_root_item(instance),
            'hierarchy_tree': self.get_hierarchical_structure(instance)
        })

    def get_root_item(self, item):
        """
        Recursively find the root item of the given `MenuItem`.

        Args:
            item (MenuItem): The `MenuItem` instance whose root is to be found.

        Returns:
            str: The name of the root `MenuItem`.
        """
        while item.parent:
            item = item.parent
        return item.name

    @swagger_auto_schema(
        request_body=MenuItemSerializer,
        responses={201: openapi.Response('Created', MenuItemSerializer)},
        operation_description="Create a new `MenuItem` instance. Calculate the depth based on the parent item."
    )
    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        parent_id = data.get('parent', None)
        if parent_id:
            try:
                parent = MenuItem.objects.get(id=parent_id)
                data['depth'] = parent.depth + 1
            except MenuItem.DoesNotExist:
                return Response({'error': 'Parent item does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            data['depth'] = 0

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(
        responses={
            200: openapi.Response('Success', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'data': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=get_menu_item_schema()
                    ),
                    'hierarchy_tree': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'depth': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'children': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(type=openapi.TYPE_OBJECT)
                                )
                            }
                        )
                    )
                }
            ))
        },
        operation_description="List all `MenuItem` instances with hierarchical structure."
    )
    def list(self, request, *args, **kwargs):
        response = super(MenuItemViewSet, self).list(request, *args, **kwargs)
        return Response({
            'data': response.data,
            'hierarchy_tree': self.get_hierarchical_structure()
        })

    def get_hierarchical_structure(self, root_item=None):
        """
        Build a hierarchical structure of `MenuItem` instances, including the root item if provided.

        Args:
            root_item (MenuItem, optional): The root item to start building the structure from.

        Returns:
            list: A nested list representing the hierarchical structure of `MenuItem` objects.
        """
        def build_tree(item):
            tree = {
                'id': item.id,
                'name': item.name,
                'parent': item.parent.name if item.parent is not None else None,
                'depth': item.depth,
                'children': []
            }
            children = MenuItem.objects.filter(parent=item)
            for child in children:
                tree['children'].append(build_tree(child))
            return tree

        if root_item is None:
            top_level_items = MenuItem.objects.filter(parent__isnull=True)
            return [build_tree(item) for item in top_level_items]
        else:
            return [build_tree(root_item)]

    @swagger_auto_schema(
        responses={204: 'No Content', 400: 'Bad Request'},
        operation_description="Delete a specific `MenuItem` instance. Ensure that it does not have any children before deletion."
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.children.exists():
            return Response({'error': 'Cannot delete a parent item with children.'}, status=status.HTTP_400_BAD_REQUEST)
        return super(MenuItemViewSet, self).destroy(request, *args, **kwargs)
