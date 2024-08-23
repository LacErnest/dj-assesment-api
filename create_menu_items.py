import django
import os
import random
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "assesment_api.settings")
django.setup()

from menu_hierarchy.models import MenuItem

fake = Faker()

def create_menu_items(num_items=50):
    root = MenuItem.objects.create(name="Root Menu")
    print(f"Created root item: {root.name}")

    items = [root]

    for i in range(1, num_items):
        parent = random.choice(items)
        
        item = MenuItem.objects.create(
            name=fake.unique.word().capitalize(),
            parent=parent
        )
        items.append(item)
        print(f"Created item: {item.name} (Parent: {item.parent.name}, Depth: {item.depth})")

    print(f"\nCreated {num_items} menu items (including root).")

    print("\nMenu Hierarchy:")
    print_hierarchy(root)

def print_hierarchy(item, level=0):
    print("  " * level + f"- {item.name} (Depth: {item.depth})")
    for child in item.children.all():
        print_hierarchy(child, level + 1)

if __name__ == "__main__":
    create_menu_items()