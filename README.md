# Workspace Administration Tool (WAT)

A streamlined command-line interface wrapping the power of [GAM (Google Apps Manager)](https://github.com/GAM-team/GAM/wiki) for day‑to‑day Google Workspace administration. WAT allows administrators to manage users, groups, Drive files, and an employee database from a unified CLI menu.

---

## Features

* **User Management**

  * Create, update (rename, move org unit, reset password), suspend/reactivate, delete/undelete users
  * Modify Gmail settings (IMAP, POP, signatures, forwarding)
  * Lookup user info and groups

* **Group Management**

  * Create and delete groups
  * Add or remove members (with roles: member/manager/owner)
  * List group members

* **Drive Management**

  * List all files owned by a user (with optional CSV export)
  * Transfer file ownership (single file or bulk via CSV)

* **Employee Database**

  * Fetch users directly from Workspace
  * Import/export from CSV
  * Manual add/remove and in-memory listing

---

## Prerequisites

1. **Python 3.7+**
2. **[GAM](https://github.com/GAM-team/GAM)** installed and configured with Workspace admin credentials
3. **prompt\_toolkit** Python library for interactive prompts

```bash
pip install prompt_toolkit
```

Ensure your `gam` binary is on your `PATH` and that you can run `gam info user <email>` successfully.

---

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/your-org/wat.git
   cd wat
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Make the main script executable:

   ```bash
   chmod +x wat.py
   ```

---

## Configuration

- Verify your GAM setup:

  ```bash
  gam info domain
  ```

- If you need custom GAM args (e.g. service account), update the `gam` command calls in `wat.py` accordingly.

---

## Usage

Run the tool:

```bash
./wat.py
```

You’ll be presented with a top‑level menu:

```
--- MAIN MENU ---
1. User Management
2. Group Management
3. Drive Management
4. Employee DB
0. Exit
```

Navigate to the desired section and follow prompts.

### Common Workflows

* **Create a new user**:

  1. Select `1. User Management` → `1. Create user`
  2. Enter primary email, first/last name, and optional password.

* **Suspend/reactivate a user**:

  1. `1. User Management` → `4. Suspend user` or `5. Reactivate user`

* **Add a member to a group**:

  1. `2. Group Management` → `3. Add member to group`
  2. Provide group email, user email, and role.

* **Transfer Drive file ownership**:

  1. `3. Drive Management` → `2. Transfer ownership`
  2. Choose single file or CSV bulk.

---

## Developer Notes

* All GAM commands are invoked via `subprocess.run(...)`.
* Employee list is fetched at startup; auto-complete via `prompt_toolkit`.
* ANSI colors improve readability — adjust or remove color codes as desired.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Commit your changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feat/your-feature`)
5. Open a Pull Request

Please adhere to existing code style and add appropriate tests/documentation.

---

## License

MIT License © 2025 bytewyseIT

---

## Contact

Project maintained by [bytewyseIT](https://github.com/bytewyseIT).
For issues or questions, please open an issue on GitHub.
