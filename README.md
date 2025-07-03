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

---

## Function Reference

This section provides detailed documentation for all functions in the Workspace Administration Tool.

### Core Utility Functions

#### `display_header()`
**Purpose**: Displays the ASCII logo and script metadata when the tool starts.
**Functionality**: 
- Prints the custom ASCII art logo in cyan color
- Shows script name, version, author, and contact information
- Called at the beginning of the main function

#### `fetch_employees_from_gworkspace()`
**Purpose**: Retrieves all users from Google Workspace and populates the in-memory employee list.
**Functionality**:
- Executes `gam print users fields primaryemail,firstname,lastname`
- Parses CSV output to extract email, first name, and last name
- Creates formatted names (e.g., "John Doe") from first and last names
- Stores employee data in the global `employees` list
- Provides feedback on success/failure with color-coded messages
**GAM Command**: `gam print users fields primaryemail,firstname,lastname`

#### `get_employee_name()`
**Purpose**: Provides interactive employee selection with auto-completion.
**Functionality**:
- Uses `prompt_toolkit` for enhanced command-line interface
- Implements auto-completion for employee names and emails
- Returns selected employee name (parsed from "Name <email>" format)
- Integrates with `EmployeeCompleter` class for suggestions

#### `get_employee_email(name)`
**Purpose**: Converts employee name to email address.
**Functionality**:
- Searches the in-memory employee list for matching names
- Performs case-insensitive matching
- Returns the corresponding email address or None if not found
- Displays error message if employee is not found

### Employee Database Management

#### `EmployeeCompleter` Class
**Purpose**: Provides auto-completion functionality for employee selection.
**Functionality**:
- Inherits from `prompt_toolkit.completion.Completer`
- Generates completion suggestions based on employee names and emails
- Filters suggestions based on user input (case-insensitive)
- Returns formatted suggestions as "Name <email>"

### Drive Management Functions

#### `list_files()`
**Purpose**: Lists all files owned by a specific user with optional CSV export.
**Functionality**:
1. Prompts for employee name with auto-completion
2. Executes `gam user <email> show filelist`
3. Parses CSV output and displays in formatted table
4. Offers CSV export functionality
5. Handles errors gracefully with color-coded messages
**GAM Command**: `gam user <email> show filelist`
**CSV Export**: Includes all file metadata (name, size, permissions, etc.)

#### `transfer_ownership()`
**Purpose**: Transfers file ownership between users.
**Functionality**:
1. Prompts for source and destination employees
2. Offers two transfer modes:
   - **Single file**: Transfer by file ID
   - **Bulk via CSV**: Transfer multiple files using CSV file
3. Executes appropriate GAM command based on selection
**GAM Commands**:
- Single: `gam user <source> transfer file <fileid> to <destination>`
- Bulk: `gam user <source> transfer drivefile csv <csvfile> to <destination>`

### User Management Functions

#### `create_user()`
**Purpose**: Creates a new Google Workspace user account.
**Functionality**:
1. Prompts for primary email address
2. Collects first and last names
3. Optionally sets password (auto-generated if blank)
4. Executes GAM create user command
**GAM Command**: `gam create user <email> firstname <first> lastname <last> [password <password>]`

#### `update_user()`
**Purpose**: Updates existing user information.
**Functionality**:
1. Prompts for employee name with auto-completion
2. Offers three update options:
   - **Rename**: Update first and last names
   - **Move OU**: Change organizational unit
   - **Change password**: Set new password and force change
3. Executes appropriate GAM command based on selection
**GAM Commands**:
- Rename: `gam update user <email> firstname <first> lastname <last>`
- Move OU: `gam update user <email> org <orgunit>`
- Password: `gam update user <email> password <password> changepassword on`

#### `modify_gmail_settings()`
**Purpose**: Modifies various Gmail settings for a user.
**Functionality**:
1. Prompts for employee name with auto-completion
2. Offers four Gmail setting options:
   - **IMAP**: Enable/disable IMAP access
   - **POP**: Enable/disable POP access
   - **Signature**: Set email signature (text or file)
   - **Forwarding**: Configure email forwarding
3. Handles signature input intelligently (detects file vs text)
4. Executes appropriate GAM command based on selection
**GAM Commands**:
- IMAP: `gam user <email> imap <on/off>`
- POP: `gam user <email> pop <on/off>`
- Signature: `gam user <email> signature <text>` or `gam user <email> signature file <filepath>`
- Forwarding: `gam user <email> forward to <email> keepcopy on` or `gam user <email> clear forward`

#### `suspend_user()`
**Purpose**: Suspends a user account (prevents login and access).
**Functionality**:
1. Prompts for employee name with auto-completion
2. Executes GAM command to suspend the user
**GAM Command**: `gam update user <email> suspended on`

#### `reactivate_user()`
**Purpose**: Reactivates a previously suspended user account.
**Functionality**:
1. Prompts for employee name with auto-completion
2. Executes GAM command to reactivate the user
**GAM Command**: `gam update user <email> suspended off`

#### `delete_user()`
**Purpose**: Permanently deletes a user account.
**Functionality**:
1. Prompts for employee name with auto-completion
2. Executes GAM command to delete the user
**GAM Command**: `gam delete user <email>`

#### `undelete_user()`
**Purpose**: Restores a previously deleted user account.
**Functionality**:
1. Prompts for the user's unique ID (required for undelete)
2. Executes GAM command to undelete the user
**GAM Command**: `gam undelete user <uniqueid>`

#### `lookup_user_full_info()`
**Purpose**: Displays comprehensive user information and group memberships.
**Functionality**:
1. Prompts for employee name with auto-completion
2. Fetches and displays detailed user information
3. Retrieves and parses group membership data
4. Displays groups in formatted table with color-coded roles
5. Offers CSV export of group memberships
6. Provides summary statistics
**GAM Commands**:
- User info: `gam info user <email>`
- Groups: `gam user <email> print groups`
**Features**:
- Color-coded role display (Green=Owner, Yellow=Manager, Cyan=Member)
- CSV export with all group details
- Error handling and validation

### Group Management Functions

#### `create_group()`
**Purpose**: Creates a new Google Workspace group.
**Functionality**:
1. Prompts for group email address
2. Optionally collects group name and description
3. Executes GAM command to create the group
**GAM Command**: `gam create group <email> [name <name>] [description <desc>]`

#### `delete_group()`
**Purpose**: Permanently deletes a Google Workspace group.
**Functionality**:
1. Prompts for group email address
2. Executes GAM command to delete the group
**GAM Command**: `gam delete group <email>`

#### `add_user_to_group()`
**Purpose**: Adds users to a group with role assignment.
**Functionality**:
1. Prompts for group email address
2. Offers two addition modes:
   - **Single user**: Add one user with role
   - **Bulk via CSV**: Add multiple users from CSV file
3. For single user: prompts for user email and role
4. For bulk: processes CSV file with validation
5. Provides real-time feedback and summary statistics
**GAM Command**: `gam update group <group> add <role> user <email>`
**CSV Format**: `email,role` (role defaults to "member" if omitted)
**Features**:
- Email validation
- Error handling and reporting
- Success/failure counting
- Color-coded feedback

#### `remove_user_from_group()`
**Purpose**: Removes users from a group.
**Functionality**:
1. Prompts for group email address
2. Offers two removal modes:
   - **Single user**: Remove one user
   - **Bulk via CSV**: Remove multiple users from CSV file
3. For single user: prompts for user email and role
4. For bulk: processes CSV file with validation
5. Provides real-time feedback and summary statistics
**GAM Command**: `gam update group <group> remove <role> user <email>`
**CSV Format**: `email,role` (role defaults to "member" if omitted)
**Features**:
- Email validation
- Error handling and reporting
- Success/failure counting
- Color-coded feedback

#### `list_group_members()`
**Purpose**: Lists all members of a specific group.
**Functionality**:
1. Prompts for group email address
2. Executes GAM command to list group members
3. Displays member information with roles
**GAM Command**: `gam print group-members group <email> fields email,role`

### Menu Management Functions

#### `user_management_menu()`
**Purpose**: Provides the user management submenu interface.
**Functionality**:
- Displays user management options
- Handles user input and calls appropriate functions
- Implements infinite loop with exit option
- Provides error handling for invalid selections

#### `group_management_menu()`
**Purpose**: Provides the group management submenu interface.
**Functionality**:
- Displays group management options
- Handles user input and calls appropriate functions
- Implements infinite loop with exit option
- Provides error handling for invalid selections

#### `drive_management_menu()`
**Purpose**: Provides the drive management submenu interface.
**Functionality**:
- Displays drive management options
- Handles user input and calls appropriate functions
- Implements infinite loop with exit option
- Provides error handling for invalid selections

#### `employee_management_menu()`
**Purpose**: Provides the employee database management submenu interface.
**Functionality**:
- Displays employee database options
- Returns user selection for processing
- Note: Some employee management functions are referenced but not fully implemented

#### `main()`
**Purpose**: Main application entry point and primary menu system.
**Functionality**:
1. Displays application header
2. Fetches employees from Google Workspace on startup
3. Implements main menu loop with four primary sections:
   - User Management
   - Group Management
   - Drive Management
   - Employee DB
4. Handles menu navigation and function calls
5. Provides graceful exit functionality

### Error Handling and User Experience

The tool implements comprehensive error handling throughout:

- **Color-coded feedback**: Green for success, red for errors, yellow for warnings
- **Input validation**: Email format checking, file existence validation
- **Graceful failures**: Functions exit cleanly when errors occur
- **User feedback**: Clear messages for all operations
- **Progress indicators**: Real-time updates for bulk operations

### GAM Integration

All functions utilize GAM (Google Apps Manager) for Google Workspace administration:

- **Command execution**: Uses `subprocess.run()` for GAM command execution
- **Output parsing**: Handles CSV output from GAM commands
- **Error capture**: Captures and displays GAM error messages
- **Documentation**: Includes GAM documentation links in comments

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
