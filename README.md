# Menu Hierarchy API

This API manages a hierarchical menu structure using Django.

## MenuItem Model

The `MenuItem` represents a single item in the menu hierarchy.

### Fields:
- `id`: UUID (primary key)
- `name`: String (max 255 characters)
- `parent`: ForeignKey to self (optional)
- `depth`: Integer
- `created_at`: DateTime
- `updated_at`: DateTime

### Features:
- Automatic depth calculation on save
- Indexed fields for optimized queries
- Parent name accessor

## Scripts

### create_menu_items.py

This script generates a sample menu hierarchy:

- Creates a root menu item
- Generates a specified number of menu items (default: 50)
- Randomly assigns parents to create a hierarchy
- Prints the created hierarchy

Usage:

`python create_menu_items.py`

## Tests

The `tests.py` file contains unit tests for the API. Run tests using:

`python manage.py test`


