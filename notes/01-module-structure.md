# Topic 1: Odoo Module Structure

## 📋 Overview
An Odoo module is a directory containing Python code, XML files, and other resources that add functionality to Odoo. Every module follows a standard structure.

## 🗂️ Standard Module Structure

```
module_name/
├── __init__.py              # Python package initializer
├── __manifest__.py          # Module metadata and configuration
├── models/                  # Python models (business logic)
│   ├── __init__.py
│   └── model_name.py
├── views/                   # XML view definitions
│   ├── menu_views.xml
│   └── model_views.xml
├── security/                # Access control
│   ├── ir.model.access.csv  # CRUD permissions
│   └── ir_rules.xml         # Record-level security
├── data/                    # Data files (loaded at install)
│   └── data.xml
├── demo/                    # Demo data (optional)
│   └── demo.xml
├── wizard/                  # Transient models (wizards/dialogs)
│   ├── __init__.py
│   └── wizard_name.py
├── report/                  # Report templates
│   └── report_template.xml
├── static/                  # Frontend assets
│   ├── src/
│   │   ├── js/             # JavaScript files
│   │   ├── css/            # Stylesheets
│   │   └── xml/            # QWeb templates
│   └── description/
│       └── icon.png        # Module icon
├── controllers/             # HTTP controllers
│   ├── __init__.py
│   └── main.py
├── tests/                   # Unit tests
│   ├── __init__.py
│   └── test_*.py
└── i18n/                    # Translations
    ├── module_name.pot      # Translation template
    └── language_code.po     # Language translations
```

## 📄 The __manifest__.py File

This is the **most important file** - it defines your module to Odoo.

### Example from Sale module:

```python
{
    # Basic Information
    'name': 'Sales',                    # Display name
    'version': '1.2',                   # Module version
    'category': 'Sales/Sales',          # Category in Apps menu
    'summary': 'Sales internal machinery',  # Short description
    
    # Full description (supports reStructuredText)
    'description': """
    This module contains all the common features of Sales Management.
    """,
    
    # Dependencies - modules that MUST be installed first
    'depends': [
        'sales_team',      # Must be installed before this module
        'account_payment',
        'utm',
    ],
    
    # Data files - loaded in this ORDER during installation
    'data': [
        # 1. Security first (users need permissions to access data)
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'security/ir_rules.xml',
        
        # 2. Reports
        'report/sale_report_views.xml',
        
        # 3. Data files (master data, sequences, etc.)
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        
        # 4. Wizard views
        'wizard/sale_make_invoice_advance_views.xml',
        
        # 5. Model views
        'views/sale_order_views.xml',
        'views/res_partner_views.xml',
        
        # 6. Menus last (they reference actions from views)
        'views/sale_menus.xml',
    ],
    
    # Demo data - only loaded if you enable demo data
    'demo': [
        'data/sale_demo.xml',
    ],
    
    # Module state
    'installable': True,        # Can be installed
    'auto_install': False,      # Install automatically if dependencies met
    'application': True,        # Is a full application (shows in Apps)
    
    # Web assets (JavaScript, CSS, etc.)
    'assets': {
        'web.assets_backend': [  # Backend (Odoo interface)
            'sale/static/src/js/**/*',
            'sale/static/src/scss/**/*',
        ],
        'web.assets_frontend': [ # Frontend (website)
            'sale/static/src/js/frontend/**/*',
        ],
    },
    
    # License
    'license': 'LGPL-3',
}
```

## 🔑 Key Manifest Keys Explained

### Required Keys:
- **name**: Module display name
- **depends**: List of module dependencies (base is implicit)

### Common Keys:
- **data**: XML/CSV files to load (order matters!)
- **installable**: Whether module can be installed
- **application**: If True, shows as main app in Apps menu
- **auto_install**: Install automatically when all dependencies are present

### Optional Keys:
- **version**: Module version (format: x.y or x.y.z)
- **category**: Where it appears in Apps menu
- **summary**: One-line description
- **description**: Full description (supports Markdown/RST)
- **author**: Author name
- **website**: Module website URL
- **demo**: Demo data files
- **assets**: Frontend JavaScript/CSS bundles
- **license**: License type (LGPL-3, AGPL-3, etc.)
- **external_dependencies**: Python packages needed
- **images**: Screenshots for App store

## 📂 Directory Purposes

### models/
Contains Python files defining your database models (tables). Each model is a Python class.

**Example:** `models/sale_order.py` defines the `sale.order` model.

### views/
Contains XML files defining the user interface:
- Form views (detail view)
- Tree views (list view)
- Kanban views (card view)
- Search views (filters and grouping)
- Actions (what happens when you click something)
- Menus (navigation structure)

### security/
Access control files:
- **ir.model.access.csv**: CRUD permissions (Create/Read/Update/Delete) by user group
- **ir_rules.xml**: Row-level security (which records users can see)

### data/
Data loaded during installation:
- Sequences (auto-incrementing numbers)
- Email templates
- Cron jobs (scheduled tasks)
- System parameters
- Initial records

### wizard/
Transient models (temporary data) for dialogs and wizards.

### static/
All frontend files:
- JavaScript
- CSS/SCSS
- Images
- XML templates (QWeb)

### controllers/
HTTP endpoints (web routes) for handling web requests.

### tests/
Python unit tests for your module.

### i18n/
Translation files for internationalization.

## 🎯 Module Loading Order

When Odoo loads your module:

1. **Dependencies checked** - All modules in `depends` must be installed
2. **Python code loaded** - `__init__.py` imports your models
3. **Database tables created** - Based on your models
4. **Data files loaded** - In the order listed in `'data'` key
5. **Module marked installed** - Ready to use!

## ✅ Best Practices

1. **Always specify dependencies** - Even if module seems to work without them
2. **Order matters in data list** - Security first, menus last
3. **Use clear directory structure** - Follow conventions
4. **One model per file** - Keep files focused
5. **Name files clearly** - `sale_order.py`, not `so.py`

## 🔍 Real Example: Sale Module Structure

```
sale/
├── __init__.py
├── __manifest__.py          ✅ Defines the module
├── models/
│   ├── __init__.py
│   ├── sale_order.py        # Main sales order model
│   ├── sale_order_line.py   # Order line items
│   └── res_partner.py       # Extends customer model
├── views/
│   ├── sale_order_views.xml     # Forms, trees, search
│   ├── sale_portal_templates.xml
│   └── sale_menus.xml       # Navigation menus
├── security/
│   ├── ir.model.access.csv  # Who can create/read/write/delete
│   └── ir_rules.xml         # Row-level rules
├── wizard/
│   └── sale_make_invoice_advance_views.xml
├── report/
│   └── sale_report_templates.xml
├── data/
│   ├── mail_template_data.xml
│   └── ir_sequence_data.xml
└── static/
    └── src/
        └── js/
            └── sale_action_helper/
```

## 💡 Key Takeaways

1. **__manifest__.py is mandatory** - Odoo won't recognize your module without it
2. **Structure is standardized** - Follow conventions for maintainability
3. **Dependencies are critical** - Always list what you depend on
4. **Load order matters** - Security before data, menus last
5. **Every module is a Python package** - Must have __init__.py

## 🎓 What's Next?

Now that you understand module structure, next we'll dive into:
- **BaseModel & ORM** - How to define database models
- **Field Types** - Different types of data you can store
- **CRUD Operations** - Creating, reading, updating, deleting records

---

**Source:** Odoo 19.0 - addons/sale/
**Date:** 2026-03-27
