# 🔐 TOPIC 7: SECURITY SYSTEM IN ODOO (COMPREHENSIVE)

**Core files studied:**
- `/home/precious/Desktop/odoo-19.0/odoo/addons/base/models/ir_model.py`
- `/home/precious/Desktop/odoo-19.0/odoo/addons/base/models/ir_rule.py`
- `/home/precious/Desktop/odoo-19.0/odoo/orm/models.py`
- `/home/precious/Desktop/odoo-19.0/odoo/addons/base/security/base_groups.xml`
- `/home/precious/Desktop/odoo-19.0/odoo/addons/base/security/base_security.xml`
- `/home/precious/Desktop/odoo-19.0/odoo/addons/base/security/ir.model.access.csv`
- `/home/precious/Desktop/odoo-19.0/addons/sale/security/ir.model.access.csv`
- `/home/precious/Desktop/odoo-19.0/addons/sale/security/ir_rules.xml`
- `/home/precious/Desktop/odoo-19.0/addons/project/security/ir.model.access.csv`
- `/home/precious/Desktop/odoo-19.0/addons/project/security/project_security.xml`

---

## 1) Security mental model (must memorize)

Odoo security is **layered**. A request passes through these checks:

1. **Model-level ACLs** (`ir.model.access`)
2. **Record rules** (`ir.rule`, row-level domain filtering)
3. **Field-level groups** (`groups=...` on fields)

And there is one special bypass:

- **Superuser / sudo** bypasses normal ACL and rule checks.

If any layer blocks access, operation fails.

---

## 2) The exact enforcement path in core ORM

From `odoo/orm/models.py`:

- `check_access(operation)` calls `_check_access(operation)`
- `_check_access` first checks ACL via `ir.model.access.check(...)`
- then computes record rule domain via `ir.rule._compute_domain(...)`
- then filters forbidden records and raises access error if needed

### Important core behavior

In `_check_access`:

- ACL check happens first (`ir.model.access`)
- Record rule check happens only for real records (`if any(self._ids):`)

For **create**, Odoo does both:

1. Pre-check ACL before insert (`self.check_access('create')`)
2. Post-check rules on created records (`records.check_access('create')`)

So `perm_create` rules can still block creation after values are set.

---

## 3) Layer A: ACLs (`ir.model.access`)

ACLs answer:

> "Can this group perform read/write/create/delete on this model at all?"

### File format (usually CSV)

`security/ir.model.access.csv` columns:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
```

Example (from `sale/security/ir.model.access.csv`):

```csv
access_sale_order,sale.order,model_sale_order,sales_team.group_sale_salesman,1,1,1,0
access_sale_order_manager,sale.order.manager,model_sale_order,sales_team.group_sale_manager,1,1,1,1
```

Meaning:

- Salesman: can read/write/create sale orders, cannot delete.
- Sales Manager: full CRUD on sale orders.

### ACL rules to remember

1. ACL is **model-level** only, not per-record.
2. If no ACL grants access for an operation, it is denied.
3. ACLs from multiple groups are cumulative (granting).
4. `group_id` empty means "global" ACL (applies to all users) and is generally risky.

From base code (`ir_model.py`), ACL decision is cached and based on:
- current user groups
- operation (`read`, `write`, `create`, `unlink`)

---

## 4) Layer B: Record Rules (`ir.rule`)

Record rules answer:

> "For allowed model operations, which specific rows can this user touch?"

Rule field highlights (`ir_rule.py`):

- `model_id`
- `domain_force` (domain expression string)
- `groups` (optional)
- `perm_read`, `perm_write`, `perm_create`, `perm_unlink`

### Rule combination logic (critical)

From `ir_rule.py` `_compute_domain`:

- **Global rules** (no groups) are combined with **AND**
- **Group rules** (matching current user groups) are combined with **OR**
- Final domain is:
  - `AND(all global domains, OR(all matching group domains))` (if group domains exist)
  - otherwise just `AND(all global domains)`

This is one of the most important Odoo security facts.

### Real examples

#### Sale multi-company rule
From `sale/security/ir_rules.xml`:

```xml
<record id="sale_order_comp_rule" model="ir.rule">
    <field name="model_id" ref="model_sale_order"/>
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
</record>
```

#### Personal salesman visibility

```xml
<record id="sale_order_personal_rule" model="ir.rule">
    <field name="model_id" ref="model_sale_order"/>
    <field name="domain_force">['|',('user_id','=',user.id),('user_id','=',False)]</field>
    <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
</record>
```

#### Manager sees all

```xml
<record id="sale_order_see_all" model="ir.rule">
    <field name="model_id" ref="model_sale_order"/>
    <field name="domain_force">[(1,'=',1)]</field>
    <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman_all_leads'))]"/>
</record>
```

---

## 5) Layer C: Field-level security (`groups` on fields)

Even if ACL + record rule allow a record, specific fields may still be blocked.

From ORM (`models.py`):

- `_has_field_access` checks `field.groups`
- `_check_field_access` raises `AccessError` if user lacks field group

Example from modules:

```python
has_work_permit = fields.Binary(string="Work Permit", groups="hr.group_hr_user")
```

Only users in `hr.group_hr_user` can read/write that field.

---

## 6) `res.groups` and implied permissions

Groups are defined in XML (`res.groups`).

Important base examples (`base_groups.xml`):

- `base.group_user` (internal user)
- `base.group_portal`
- `base.group_public`
- `base.group_erp_manager`
- `base.group_system`

### `implied_ids`

If group A implies group B, a user in A automatically gets B's permissions.

Example:

```xml
<record model="res.groups" id="group_system">
    <field name="implied_ids" eval="[Command.link(ref('group_erp_manager'))]"/>
</record>
```

So system admins inherit access rights manager capabilities.

---

## 7) Common security patterns in standard modules

### Pattern 1: Multi-company isolation

```xml
[('company_id', 'in', company_ids + [False])]
```

Seen in `project_security.xml`, `base_security.xml`.

### Pattern 2: "Own records only" for transient/wizard

```xml
[('create_uid', '=', user.id)]
```

Used for wizards and user-specific temp data.

### Pattern 3: Portal partner scoping

```xml
[('partner_id','child_of',[user.commercial_partner_id.id])]
```

Used in sale portal rules.

### Pattern 4: Manager sees everything

```xml
[(1, '=', 1)]
```

Assigned only to manager/admin groups.

### Pattern 5: Read-only rule

Use rule permissions to disable specific operations:

```xml
<field name="perm_write" eval="False"/>
<field name="perm_create" eval="False"/>
<field name="perm_unlink" eval="False"/>
```

Seen in project portal/task visibility rules.

---

## 8) Security file load order in manifest

In module `__manifest__.py`, security files are usually loaded before views/menus.

From `sale/__manifest__.py`:

```python
'data': [
    'security/ir.model.access.csv',
    'security/res_groups.xml',
    'security/ir_rules.xml',
    ...
]
```

From `project/__manifest__.py`:

```python
'data': [
    'security/project_security.xml',
    'security/ir.model.access.csv',
    'security/ir.model.access.xml',
    ...
]
```

If security isn't loaded early, users can hit broken menus/actions.

---

## 9) ACL vs Record Rule: exact difference

| Aspect | ACL (`ir.model.access`) | Record Rule (`ir.rule`) |
|---|---|---|
| Scope | Model-level | Record-level |
| Purpose | Allow/deny operation type on model | Restrict visible/editable rows |
| Storage | CSV/XML | XML/UI record |
| Logic | Union of allowed groups | Global AND + Group OR |
| Typical file | `ir.model.access.csv` | `ir_rules.xml`, `*_security.xml` |

### Practical consequence

User needs **both**:

1. ACL permission for operation (e.g. write)
2. Rule domain matching target record for that operation

If either fails, operation fails.

---

## 10) Building security for your own custom module

Assume module: `library_management`
Models:
- `library.book`
- `library.borrowing`

Groups:
- `library.group_library_user`
- `library.group_library_manager`

### A) `security/library_security.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="group_library_user" model="res.groups">
        <field name="name">Library User</field>
        <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
    </record>

    <record id="group_library_manager" model="res.groups">
        <field name="name">Library Manager</field>
        <field name="implied_ids" eval="[(4, ref('library_management.group_library_user'))]"/>
    </record>

    <!-- Multi-company -->
    <record id="library_book_company_rule" model="ir.rule">
        <field name="name">Library Book multi-company</field>
        <field name="model_id" ref="model_library_book"/>
        <field name="domain_force">[('company_id', 'in', company_ids + [False])]</field>
    </record>

    <!-- Users only see their own borrowings -->
    <record id="library_borrowing_own_rule" model="ir.rule">
        <field name="name">Borrowings: own records</field>
        <field name="model_id" ref="model_library_borrowing"/>
        <field name="domain_force">[('user_id', '=', user.id)]</field>
        <field name="groups" eval="[(4, ref('library_management.group_library_user'))]"/>
    </record>

    <!-- Managers see all borrowings -->
    <record id="library_borrowing_manager_rule" model="ir.rule">
        <field name="name">Borrowings: manager all</field>
        <field name="model_id" ref="model_library_borrowing"/>
        <field name="domain_force">[(1, '=', 1)]</field>
        <field name="groups" eval="[(4, ref('library_management.group_library_manager'))]"/>
    </record>
</odoo>
```

### B) `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_library_book_user,library.book.user,model_library_book,library_management.group_library_user,1,0,0,0
access_library_book_manager,library.book.manager,model_library_book,library_management.group_library_manager,1,1,1,1
access_library_borrowing_user,library.borrowing.user,model_library_borrowing,library_management.group_library_user,1,1,1,0
access_library_borrowing_manager,library.borrowing.manager,model_library_borrowing,library_management.group_library_manager,1,1,1,1
```

### C) Manifest order

```python
'data': [
    'security/library_security.xml',
    'security/ir.model.access.csv',
    'views/library_book_views.xml',
    'views/library_menus.xml',
]
```

---

## 11) Typical mistakes (and how to avoid them)

### Mistake 1: ACL exists, but no matching record rule

Symptom: user can open model but sees zero records.

Fix: verify record rule domains for that user/group.

### Mistake 2: Record rule too broad (`[(1,'=',1)]`) for normal users

Symptom: users see data they should not.

Fix: use group-specific all-access only for manager/admin groups.

### Mistake 3: Missing multi-company filter

Symptom: users see other company data.

Fix: add `company_ids` domain patterns.

### Mistake 4: Security file order in manifest

Symptom: menus/actions accessible but permissions broken.

Fix: load security files before views/menus.

### Mistake 5: Wrong external IDs (`model_id`, `group_id`)

Symptom: install/update errors or silently ineffective rules.

Fix: verify XML IDs exactly (`model_xxx`, `module.group_xxx`).

### Mistake 6: Overusing `sudo()` in business logic

Symptom: code bypasses intended security boundaries.

Fix: use `sudo()` only where absolutely required and controlled.

---

## 12) How to debug security problems

When you hit `AccessError`, debug in this order:

1. **Check ACL first**
   - Does user have model CRUD for this operation?
2. **Check record rule domain**
   - Does record satisfy final computed domain?
3. **Check field groups**
   - Is blocked field restricted by `groups=...`?
4. **Check user groups**
   - Includes implied groups?
5. **Check company context**
   - `allowed_company_ids`, active company switch

### Useful places in source

- ACL check: `ir_model.py` (`IrModelAccess.check`)
- Rule domain merge: `ir_rule.py` (`_compute_domain`)
- ORM enforcement: `models.py` (`_check_access`, `_check_field_access`)

---

## 13) Security test checklist for every custom module

Test with at least 3 users:

1. **Normal user** (expected limited access)
2. **Manager** (expected broader access)
3. **Portal/Public** (if applicable)

For each model, test:

- read list view
- open form
- create
- edit
- delete
- cross-company visibility
- related model access through Many2one/One2many links

Also test edge cases:

- wizard records should usually be user-owned (`create_uid=user.id`)
- archived/inactive records behavior (`active_test` context)

---

## 14) Quick recap

1. ACL (`ir.model.access`) = model CRUD gate.
2. Record rule (`ir.rule`) = row-level filter by domain.
3. Field groups = field-level gate.
4. Final security is layered; all must pass.
5. Group rule logic is OR; global rule logic is AND.
6. Multi-company domains are mandatory in business apps.
7. Avoid unrestricted domains for non-manager users.

---

## 15) Practice exercise (do this next)

Create a mini security design for:

**Model:** `academy.course`
**Groups:** `academy.group_teacher`, `academy.group_academy_manager`

Requirements:

1. Teachers can read all courses, create their own, edit only courses where `teacher_id = user.id`, cannot delete.
2. Managers can fully manage all courses.
3. Add multi-company rule.
4. Add wizard model `academy.bulk.assign` accessible only to creator.

Deliverables you should write:

- `security/academy_security.xml`
- `security/ir.model.access.csv`
- manifest `data` ordering snippet

---

If you want, next we can mark this with a hands-on review format: you write your `academy_security.xml` + CSV, then I grade it line-by-line (like we did for your model exercise).
