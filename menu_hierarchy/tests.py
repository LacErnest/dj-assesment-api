from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import MenuItem
import uuid
from .serializers import MenuItemSerializer

class MenuItemViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.root_item = MenuItem.objects.create(name="Root", depth=0)
        self.child_item = MenuItem.objects.create(name="Child", parent=self.root_item, depth=1)
        self.grandchild_item = MenuItem.objects.create(name="Grandchild", parent=self.child_item, depth=2)

    def test_list_menu_items(self):
        url = reverse('menuitem-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertIn('hierarchy_tree', response.data)
        self.assertEqual(len(response.data['data']), 4)
        self.assertEqual(len(response.data['hierarchy_tree']), 1)

    def test_retrieve_menu_item(self):
        url = reverse('menuitem-detail', kwargs={'pk': self.child_item.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Child')
        self.assertEqual(response.data['depth'], 1)
        self.assertEqual(response.data['root_item'], 'Root')
        self.assertEqual(len(response.data['hierarchy_tree']), 1)

    def test_create_menu_item(self):
        url = reverse('menuitem-list')
        data = {'name': 'New Item', 'parent': self.root_item.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MenuItem.objects.count(), 4)
        self.assertEqual(response.data['depth'], 1)

    def test_create_menu_item_without_parent(self):
        url = reverse('menuitem-list')
        data = {'name': 'New Root Item'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MenuItem.objects.count(), 4)
        self.assertEqual(response.data['depth'], 0)

    def test_create_menu_item_with_nonexistent_parent(self):
        url = reverse('menuitem-list')
        data = {'name': 'New Item', 'parent': uuid.uuid4()}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_menu_item_with_children(self):
        url = reverse('menuitem-detail', kwargs={'pk': self.root_item.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_delete_menu_item_without_children(self):
        url = reverse('menuitem-detail', kwargs={'pk': self.grandchild_item.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MenuItem.objects.count(), 2)

    def test_update_menu_item(self):
        url = reverse('menuitem-detail', kwargs={'pk': self.child_item.pk})
        data = {'name': 'Updated Child'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child_item.refresh_from_db()
        self.assertEqual(self.child_item.name, 'Updated Child')

    def test_get_root_item(self):
        url = reverse('menuitem-detail', kwargs={'pk': self.grandchild_item.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['root_item'], 'Root')

    def test_hierarchical_structure(self):
        url = reverse('menuitem-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        hierarchy = response.data['hierarchy_tree']
        self.assertEqual(len(hierarchy), 1)
        self.assertEqual(hierarchy[0]['name'], 'Root')
        self.assertEqual(len(hierarchy[0]['children']), 1)
        self.assertEqual(hierarchy[0]['children'][0]['name'], 'Child')
        self.assertEqual(len(hierarchy[0]['children'][0]['children']), 1) 
        self.assertEqual(hierarchy[0]['children'][0]['children'][0]['name'], 'Grandchild')