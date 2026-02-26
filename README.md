# Permission Studio

**A visual permission debugger for Frappe / ERPNext.**

One page. Three views. Zero guesswork.

Permission Studio gives System Managers a single dashboard to visualize, trace, and understand the entire Frappe permission system — users, roles, DocTypes, restrictions, and document sharing — without jumping between 5 different screens.

---

## The Problem

Debugging permissions in Frappe is painful. When a user reports *"I can't see Sales Orders"*, an admin has to:

1. Open the **User** form → check assigned roles
2. Open **Role Permission Manager** → check which roles grant access to Sales Order
3. Manually cross-reference → does this user have any of those roles?
4. Check **User Permissions** → are there Company/Territory/Department restrictions?
5. Check **DocShare** → did someone share specific documents?
6. Check **Custom DocPerm** → are custom permissions overriding standard ones?

Six screens. No single source of truth. No explanation of *why* something is allowed or denied. Just trial and error.

**Permission Studio solves this in one click.**

---

## Features

### Three Matrix Views

| View | Question it answers |
|------|-------------------|
| **User View** | What can this user do across every DocType? |
| **DocType View** | Which roles have access to this DocType and at what level? |
| **Role View** | What does this role grant, across all modules? |

### Why Explainer (Permission Trace)

Click any permission cell and get a **6-step evaluation trace**:

| Step | Check |
|------|-------|
| 1 | Is the user Administrator? |
| 2 | Do the user's roles grant this permission? |
| 3 | Is it conditional on document ownership (if_owner)? |
| 4 | Are User Permission restrictions filtering access? |
| 5 | Are specific documents shared via DocShare? |
| 6 | **Final verdict: ALLOWED / CONDITIONAL / DENIED** |

Each step shows pass/fail/warn status with detailed reasoning.

### Restrictions & Shares Explorer

One dialog showing:
- All **User Permission** restrictions with affected DocTypes
- All **DocShare** records with read/write/share permissions

### 14 Permission Types Tracked

| Basic | Submittable | Special |
|-------|-------------|---------|
| Select, Read, Write, Create, Delete | Submit, Cancel, Amend | Print, Email, Report, Import, Export, Share |

### UX

- Skeleton loaders (CSS shimmer, no spinner)
- Welcome states on empty tabs
- Error states with retry buttons
- Empty data guards
- Dark mode support
- Module filtering and DocType search

---

## Installation

### Prerequisites

- Frappe Framework (v14 or v15)
- System Manager role (required to access Permission Studio)

### Install

```bash
# Navigate to your bench directory
cd /path/to/your/bench

# Get the app
bench get-app https://github.com/arshadqureshi93/permission_studio.git

# Install on your site
bench --site your-site.com install-app permission_studio

# Build assets
bench build --app permission_studio

# Clear cache
bench --site your-site.com clear-cache
```

### Access

Navigate to: **`/app/permission-studio`**

Or find it in the Frappe App Launcher.

---

## Usage Guide

### User View

1. Select the **User View** tab
2. Pick a user from the dropdown
3. Optionally filter by **Module**
4. Optionally search DocTypes by name
5. The matrix shows every DocType with 14 permission columns:
   - **✓** (green) = Allowed
   - **✗** (red) = Denied
   - **◐** (yellow) = Conditional (if_owner — only documents they created)
   - **—** = Not Applicable (e.g., Submit on non-submittable DocType)
6. **Click any cell** to open the Why Explainer
7. Click **View Restrictions** to see User Permissions and shared documents

DocTypes with active access are sorted to the top.

### DocType View

1. Select the **DocType View** tab
2. Pick a DocType from the dropdown
3. The matrix shows every role that has permissions on this DocType
4. Columns include: Role, Permission Level, If Owner, and all 14 permission types
5. Header shows whether **Custom DocPerm** is overriding standard permissions

### Role View

1. Select the **Role View** tab
2. Pick a role from the dropdown
3. All DocTypes this role has permissions for are shown, **grouped by module**
4. Header shows: total DocTypes, total modules, and user count with this role
5. Each module section has a compact permission matrix

### Why Explainer

1. In User View, click any permission cell (e.g., the "W" column on "Sales Order")
2. A dialog opens with the 6-step trace
3. Use the **Permission Type** dropdown to switch between read/write/create/delete/etc.
4. The trace re-evaluates in real time

### Restrictions & Shares Explorer

1. In User View, click the **View Restrictions** button
2. Top section shows all User Permission restrictions:
   - Summary badges (e.g., Company: "ACME Corp")
   - Cards with affected DocTypes for each restriction
3. Bottom section shows all shared documents with permission flags

---

## Architecture

### App Structure

```
permission_studio/
├── permission_studio/
│   ├── api/
│   │   ├── matrix.py           # Permission matrix computation (3 endpoints)
│   │   ├── resolver.py         # Why Explainer - 6-step trace (1 endpoint)
│   │   └── restrictions.py     # User restrictions & shares (2 endpoints)
│   │
│   ├── permission_studio/
│   │   └── page/
│   │       └── permission_studio/
│   │           ├── permission_studio.js     # Page handler
│   │           └── permission_studio.json   # Page definition (System Manager)
│   │
│   ├── public/
│   │   ├── js/
│   │   │   ├── permission_studio.bundle.js  # Main app (tabs, search, loading)
│   │   │   ├── components/
│   │   │   │   ├── matrix_view.js           # User & DocType matrices
│   │   │   │   ├── role_explorer.js         # Role view (module-grouped)
│   │   │   │   ├── why_explainer.js         # Permission trace dialog
│   │   │   │   └── user_explorer.js         # Restrictions & shares dialog
│   │   │   └── utils/
│   │   │       └── helpers.js               # Constants & utilities
│   │   └── scss/
│   │       └── permission_studio.bundle.scss
│   │
│   └── hooks.py
└── pyproject.toml
```

### API Reference

All endpoints require **System Manager** role.

#### Matrix APIs (`permission_studio.api.matrix`)

**`get_user_matrix(user, module=None)`**
Returns effective permissions for all DocTypes for a given user.

```python
# Response
{
    "user": "john@example.com",
    "roles": ["Sales User", "Accounts User"],
    "role_profile": "Sales Profile",
    "total_doctypes": 450,
    "matrix": [
        {
            "doctype": "Sales Order",
            "module": "Selling",
            "is_submittable": true,
            "permissions": {
                "select": "allow",
                "read": "allow",
                "write": "cond",    # if_owner only
                "create": "allow",
                "delete": "deny",
                "submit": "allow",
                # ... all 14 types
            }
        }
    ]
}
```

**`get_doctype_matrix(doctype)`**
Returns all roles and their permission rules for a specific DocType.

```python
# Response
{
    "doctype": "Sales Order",
    "module": "Selling",
    "is_submittable": true,
    "is_custom": false,
    "roles": [
        {
            "role": "Sales User",
            "source": "standard",
            "if_owner": false,
            "permlevel": 0,
            "permissions": { "read": 1, "write": 1, "create": 1, ... }
        }
    ]
}
```

**`get_role_matrix(role)`**
Returns all DocTypes a role can access, grouped by module.

```python
# Response
{
    "role": "Sales User",
    "user_count": 25,
    "total_doctypes": 42,
    "modules": [
        {
            "module": "Selling",
            "doctypes": [
                {
                    "doctype": "Sales Order",
                    "is_submittable": true,
                    "source": "standard",
                    "if_owner": false,
                    "permissions": { "read": 1, "write": 1, ... }
                }
            ]
        }
    ]
}
```

#### Resolver API (`permission_studio.api.resolver`)

**`explain_permission(user, doctype, ptype="read")`**
Returns step-by-step permission evaluation trace.

```python
# Response
{
    "user": "john@example.com",
    "doctype": "Sales Order",
    "ptype": "write",
    "result": "allow",        # "allow" | "deny" | "cond"
    "result_reason": "'write' allowed via role: Sales User.",
    "steps": [
        {
            "step": 1,
            "title": "Administrator Check",
            "status": "info",     # "pass" | "fail" | "warn" | "info"
            "description": "User is not Administrator — proceeding to role checks.",
            "details": []
        },
        # ... steps 2-6
    ]
}
```

#### Restrictions API (`permission_studio.api.restrictions`)

**`get_user_restrictions(user)`**
Returns all User Permission restrictions and affected DocTypes.

**`get_user_shares(user)`**
Returns all DocShare records for a user (limit 100, most recent first).

### How Permission Resolution Works

The app evaluates permissions using Frappe's actual permission system. Here's what each matrix cell value means:

| Value | Display | Meaning |
|-------|---------|---------|
| `allow` | ✓ green | At least one role grants this right unconditionally |
| `deny` | ✗ red | No role grants this right |
| `cond` | ◐ yellow | Granted only via `if_owner` — user can only access documents they created |
| `na` | — gray | Not applicable (e.g., Submit/Cancel/Amend on non-submittable DocTypes) |

The resolution logic (`_compute_effective_perms`) for each permission type:

1. Filter permission rules to only the user's roles at `permlevel = 0`
2. If any matching rule grants the right **without** `if_owner` → `allow`
3. If any matching rule grants the right **with** `if_owner` → `cond`
4. Otherwise → `deny`
5. If the right is Submit/Cancel/Amend and the DocType is not submittable → `na`

### Design Decisions

- **Read-only by design** — Permission Studio never modifies permissions. It only reads and visualizes. Safe to use in production.
- **No custom DocTypes** — The app uses only existing Frappe DocTypes (User, Role, DocPerm, Custom DocPerm, User Permission, DocShare). No database migrations needed.
- **No external dependencies** — Pure Frappe. No npm packages, no Python libraries beyond what Frappe provides.
- **Single page app** — Everything runs on one Frappe Page (`/app/permission-studio`). Components load on demand.
- **Batch queries** — `get_valid_perms(user=user)` fetches all permission rules in one query, not per-DocType. This keeps the User View fast even with 500+ DocTypes.

---

## Compatibility

| Frappe Version | Status |
|----------------|--------|
| v15 | Tested |
| v14 | Compatible |

---

## Contributing

### Setup

```bash
cd apps/permission_studio
pre-commit install
```

### Code Quality

This app uses `pre-commit` with the following tools:

- **ruff** — Python linting and formatting
- **eslint** — JavaScript linting
- **prettier** — Code formatting
- **pyupgrade** — Python syntax modernization

### Project Structure

- Backend APIs go in `permission_studio/api/`
- Frontend components go in `permission_studio/public/js/components/`
- Styles go in `permission_studio/public/scss/`
- Shared constants go in `permission_studio/public/js/utils/helpers.js`

---

## Roadmap

- [ ] Permission comparison — diff permissions between two users or roles
- [ ] Export reports — download permission matrices as PDF or Excel
- [ ] Permission audit log — track who changed what permission and when
- [ ] Inline editing — modify permissions directly from the matrix view
- [ ] Role recommendation — suggest minimal role set for a user's access needs
- [ ] Bulk permission analysis — analyze permissions across all users at once

---

## License

MIT — see [license.txt](license.txt)

---

## Author

**Arshad Qureshi** — [GitHub](https://github.com/arshadqureshi93)
