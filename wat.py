import json
import os
import subprocess
import platform
import csv
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion

# Define ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"

ascii_logo = f""" 
{CYAN} 
888       888        d8888 88888888888 
888   o   888       d88888     888     
888  d8b  888      d88P888     888     
888 d888b 888     d88P 888     888     
888d88888b888    d88P  888     888     
88888P Y88888   d88P   888     888     
8888P   Y8888  d8888888888     888     
888P     Y888 d88P     888     888  {RESET}
"""

# Script metadata
script_info = {
    "name": "Workspace Administration Tool",
    "author": "Eric Ross",
    "version": "1.0",
    "contact": "https://github.com/bytewyseIT"
}

# In-memory employee list
employees = []

def fetch_employees_from_gworkspace():
    """Fetch all users from Google Workspace via GAM"""
    global employees
    print(f"\n{YELLOW}Fetching employees from Google Workspace...{RESET}")
    try:
        command = ["gam", "print", "users", "fields", "primaryemail,firstname,lastname"]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            new_emps = []
            for line in lines[1:]:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3:
                    email, fn, ln = parts[0], parts[1], parts[2]
                    name = f"{fn} {ln}" if fn and ln else fn or ln or email.split('@')[0]
                    new_emps.append({"name": name, "email": email})
            employees = new_emps
            print(f"{GREEN}Imported {len(employees)} employees{RESET}")
        else:
            print(f"{RED}Error fetching employees: {result.stderr}{RESET}")
    except Exception as e:
        print(f"{RED}Exception: {e}{RESET}")

class EmployeeCompleter(Completer):
    """Auto-complete for employee names and emails"""
    def get_completions(self, document, complete_event):
        text = document.text.lower()
        for emp in employees:
            candidate = f"{emp['name']} <{emp['email']}>"
            if text in emp['name'].lower() or text in emp['email'].lower():
                yield Completion(candidate, start_position=-len(document.text))


def display_header():
    print(ascii_logo)
    print(f"{script_info['name']} - v{script_info['version']}")
    print(f"Author: {script_info['author']}")
    print(f"Contact: {script_info['contact']}\n")


def get_employee_name():
    completer = EmployeeCompleter()
    selected = prompt("Enter user name: ", completer=completer)
    # Parse 'Name <email>' entries
    return selected.split('<')[0].strip()


def get_employee_email(name):
    for emp in employees:
        if emp['name'].lower() == name.lower():
            return emp['email']
    print(f"{RED}No employee found for name: {name}{RESET}")
    return None

# ----- DRIVE MANAGEMENT -----
# GAM docs: https://github.com/GAM-team/GAM/wiki/Drive

def list_files():
    name = get_employee_name()
    email = get_employee_email(name)
    if not email:
        return
    cmd = ["gam", "user", email, "show", "filelist"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"{RED}Error: {res.stderr}{RESET}")
        return
    rows = [r for r in csv.reader(res.stdout.splitlines())]
    if len(rows) < 2:
        print(f"{YELLOW}No files found{RESET}")
        return
    headers, *data = rows
    widths = [max(len(cell) for cell in col) for col in zip(headers, *data)]
    print(f"\n{BLUE}" + " | ".join(h.ljust(w) for h, w in zip(headers, widths)) + f"{RESET}")
    print("-+-".join('-'*w for w in widths))
    for r in data:
        print(" | ".join(c.ljust(w) for c, w in zip(r, widths)))
    if input("\nExport to CSV? (y/n): ").lower() == 'y':
        fname = input("Filename: ").strip()
        with open(fname, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(headers)
            w.writerows(data)
        print(f"{GREEN}Exported to {fname}{RESET}")

def transfer_ownership():
    # GAM docs: https://github.com/GAM-team/GAM/wiki/Drive#transfer-drive-files
    src = get_employee_name(); dst = get_employee_name()
    e_src = get_employee_email(src); e_dst = get_employee_email(dst)
    if not e_src or not e_dst:
        return
    print("1. Single file  2. Bulk via CSV")
    choice = input("Option: ")
    if choice == '1':
        fid = input("File ID: ").strip()
        cmd = ["gam", "user", e_src, "transfer", "file", fid, "to", e_dst]
    elif choice == '2':
        csvf = input("CSV path: ").strip()
        cmd = ["gam", "user", e_src, "transfer", "drivefile", "csv", csvf, "to", e_dst]
    else:
        return
    subprocess.run(cmd)

# ----- USER MANAGEMENT -----
# GAM docs: https://github.com/GAM-team/GAM/wiki#users

def create_user():
    email = input("Primary email: ").strip()
    fn = input("First name: ").strip()
    ln = input("Last name: ").strip()
    pwd = input("Password (blank=auto): ").strip()
    cmd = ["gam", "create", "user", email, "firstname", fn, "lastname", ln]
    if pwd:
        cmd += ["password", pwd]
    subprocess.run(cmd)


def update_user():
    # rename, move OU, change password
    name = get_employee_name(); email = get_employee_email(name)
    if not email: return
    print("1. Rename  2. Move OU  3. Change password")
    c = input("Option: ")
    if c == '1':
        fn = input("New first name: ").strip()
        ln = input("New last name: ").strip()
        cmd = ["gam", "update", "user", email, "firstname", fn, "lastname", ln]
    elif c == '2':
        ou = input("Target Org Unit path: ").strip()
        cmd = ["gam", "update", "user", email, "org", ou]
    elif c == '3':
        pwd = input("New password: ").strip()
        cmd = ["gam", "update", "user", email, "password", pwd, "changepassword", "on"]
    else:
        return
    subprocess.run(cmd)


def modify_gmail_settings():
    # GAM docs: https://github.com/GAM-team/GAM/wiki/Gmail
    name = get_employee_name(); email = get_employee_email(name)
    if not email: return
    print("1.IMAP 2.POP 3.Signature 4.Forwarding")
    o = input("Option: ")
    if o == '1':
        v = input("Enable IMAP? (on/off): ").strip()
        cmd = ["gam", "user", email, "imap", v]
    elif o == '2':
        v = input("Enable POP? (on/off): ").strip()
        cmd = ["gam", "user", email, "pop", v]
    elif o == '3':
        sig = input("Signature text/file: ").strip()
        if os.path.isfile(sig):
            cmd = ["gam", "user", email, "signature", "file", sig]
        else:
            cmd = ["gam", "user", email, "signature", sig]
    elif o == '4':
        fwd = input("Forward to (email) or blank to disable: ").strip()
        if fwd:
            cmd = ["gam", "user", email, "forward", "to", fwd, "keepcopy", "on"]
        else:
            cmd = ["gam", "user", email, "clear", "forward"]
    else:
        return
    subprocess.run(cmd)


def suspend_user():
    name = get_employee_name(); email = get_employee_email(name)
    if email:
        subprocess.run(["gam", "update", "user", email, "suspended", "on"])


def reactivate_user():
    name = get_employee_name(); email = get_employee_email(name)
    if email:
        subprocess.run(["gam", "update", "user", email, "suspended", "off"])


def delete_user():
    name = get_employee_name(); email = get_employee_email(name)
    if email:
        subprocess.run(["gam", "delete", "user", email])


def undelete_user():
    uid = input("User's unique ID for undelete: ").strip()
    subprocess.run(["gam", "undelete", "user", uid])


def lookup_user_full_info():
    name = get_employee_name(); email = get_employee_email(name)
    if not email: return
    
    # Get user info
    print(f"\n{YELLOW}Fetching user information...{RESET}")
    subprocess.run(["gam", "info", "user", email])
    
    # Get user groups and display them nicely
    print(f"\n{YELLOW}Fetching user groups...{RESET}")
    result = subprocess.run(["gam", "user", email, "print", "groups"], capture_output=True, text=True)
    
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        groups_data = []
        
        # Parse the CSV output
        for line in lines:
            if line and ',' in line:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3 and parts[0] == email:
                    group_email = parts[1]
                    role = parts[2]
                    status = parts[3] if len(parts) > 3 else "ACTIVE"
                    delivery = parts[4] if len(parts) > 4 else "ALL_MAIL"
                    groups_data.append({
                        'group_email': group_email,
                        'role': role,
                        'status': status,
                        'delivery': delivery
                    })
        
        if groups_data:
            print(f"\n{BLUE}Groups for {name} ({email}):{RESET}")
            print("-" * 80)
            print(f"{'Group Email':<40} {'Role':<10} {'Status':<10} {'Delivery':<10}")
            print("-" * 80)
            
            for group in groups_data:
                role_color = GREEN if group['role'] == 'OWNER' else YELLOW if group['role'] == 'MANAGER' else CYAN
                print(f"{group['group_email']:<40} {role_color}{group['role']:<10}{RESET} {group['status']:<10} {group['delivery']:<10}")
            
            print(f"\n{BLUE}Total groups: {len(groups_data)}{RESET}")
            
            # Prompt for CSV export
            if input(f"\n{YELLOW}Export groups to CSV? (y/n): {RESET}").lower() == 'y':
                filename = input(f"{YELLOW}Enter filename (default: {name.replace(' ', '_')}_groups.csv): {RESET}").strip()
                if not filename:
                    filename = f"{name.replace(' ', '_')}_groups.csv"
                
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['User', 'Group Email', 'Role', 'Status', 'Delivery'])
                    for group in groups_data:
                        writer.writerow([email, group['group_email'], group['role'], group['status'], group['delivery']])
                
                print(f"{GREEN}Groups exported to {filename}{RESET}")
        else:
            print(f"{YELLOW}No groups found for {name}{RESET}")
    else:
        print(f"{RED}Error fetching groups: {result.stderr}{RESET}")

# ----- GROUP MANAGEMENT -----
# GAM docs: https://github.com/GAM-team/GAM/wiki/Groups

def create_group():
    grp = input("Group email: ").strip()
    nm = input("Name (opt): ").strip()
    desc = input("Description (opt): ").strip()
    cmd = ["gam", "create", "group", grp]
    if nm: cmd += ["name", nm]
    if desc: cmd += ["description", desc]
    subprocess.run(cmd)


def delete_group():
    grp = input("Group email: ").strip()
    subprocess.run(["gam", "delete", "group", grp])


def add_user_to_group():
    grp = input("Group: ").strip()
    print("1. Single user  2. Bulk via CSV")
    choice = input("Option: ")
    
    if choice == '1':
        usr = input("User to add: ").strip()
        role = input("Role (member/manager/owner) [member]: ").strip() or "member"
        cmd = ["gam", "update", "group", grp, "add", role, "user", usr]
        subprocess.run(cmd)
    elif choice == '2':
        csv_file = input("CSV file path: ").strip()
        if not os.path.exists(csv_file):
            print(f"{RED}CSV file not found: {csv_file}{RESET}")
            return
        
        print(f"{YELLOW}CSV format should be: email,role (role is optional, defaults to 'member'){RESET}")
        print(f"{YELLOW}Example: user@example.com,member{RESET}")
        
        if input(f"{YELLOW}Continue with bulk add? (y/n): {RESET}").lower() == 'y':
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    success_count = 0
                    error_count = 0
                    
                    for row_num, row in enumerate(reader, 1):
                        if len(row) >= 1:
                            user_email = row[0].strip()
                            role = row[1].strip() if len(row) > 1 else "member"
                            
                            if user_email and '@' in user_email:
                                cmd = ["gam", "update", "group", grp, "add", role, "user", user_email]
                                result = subprocess.run(cmd, capture_output=True, text=True)
                                
                                if result.returncode == 0:
                                    print(f"{GREEN}✓ Added {user_email} as {role}{RESET}")
                                    success_count += 1
                                else:
                                    print(f"{RED}✗ Failed to add {user_email}: {result.stderr.strip()}{RESET}")
                                    error_count += 1
                            else:
                                print(f"{YELLOW}⚠ Skipping invalid email on row {row_num}: {user_email}{RESET}")
                                error_count += 1
                    
                    print(f"\n{BLUE}Bulk add completed:{RESET}")
                    print(f"{GREEN}Successfully added: {success_count}{RESET}")
                    print(f"{RED}Errors: {error_count}{RESET}")
            except Exception as e:
                print(f"{RED}Error reading CSV file: {e}{RESET}")
    else:
        print("Invalid option.")


def remove_user_from_group():
    grp = input("Group: ").strip()
    print("1. Single user  2. Bulk via CSV")
    choice = input("Option: ")
    
    if choice == '1':
        usr = input("User to remove: ").strip()
        role = input("Role (member/manager/owner) [member]: ").strip() or "member"
        cmd = ["gam", "update", "group", grp, "remove", role, "user", usr]
        subprocess.run(cmd)
    elif choice == '2':
        csv_file = input("CSV file path: ").strip()
        if not os.path.exists(csv_file):
            print(f"{RED}CSV file not found: {csv_file}{RESET}")
            return
        
        print(f"{YELLOW}CSV format should be: email,role (role is optional, defaults to 'member'){RESET}")
        print(f"{YELLOW}Example: user@example.com,member{RESET}")
        
        if input(f"{YELLOW}Continue with bulk remove? (y/n): {RESET}").lower() == 'y':
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    success_count = 0
                    error_count = 0
                    
                    for row_num, row in enumerate(reader, 1):
                        if len(row) >= 1:
                            user_email = row[0].strip()
                            role = row[1].strip() if len(row) > 1 else "member"
                            
                            if user_email and '@' in user_email:
                                cmd = ["gam", "update", "group", grp, "remove", role, "user", user_email]
                                result = subprocess.run(cmd, capture_output=True, text=True)
                                
                                if result.returncode == 0:
                                    print(f"{GREEN}✓ Removed {user_email} as {role}{RESET}")
                                    success_count += 1
                                else:
                                    print(f"{RED}✗ Failed to remove {user_email}: {result.stderr.strip()}{RESET}")
                                    error_count += 1
                            else:
                                print(f"{YELLOW}⚠ Skipping invalid email on row {row_num}: {user_email}{RESET}")
                                error_count += 1
                    
                    print(f"\n{BLUE}Bulk remove completed:{RESET}")
                    print(f"{GREEN}Successfully removed: {success_count}{RESET}")
                    print(f"{RED}Errors: {error_count}{RESET}")
            except Exception as e:
                print(f"{RED}Error reading CSV file: {e}{RESET}")
    else:
        print("Invalid option.")


def list_group_members():
    grp = input("Group email: ").strip()
    # Use the correct GAM syntax for listing group members
    subprocess.run(["gam", "print", "group-members", "group", grp, "fields", "email,role"])

# ----- EMPLOYEE DB MANAGEMENT -----

def employee_management_menu():
    print(f"\n{BLUE}--- EMPLOYEE DATABASE MANAGEMENT ---{RESET}")
    print("1. Fetch employees from Google Workspace")
    print("2. Import from CSV")
    print("3. Export to CSV")
    print("4. Add manually")
    print("5. Remove")
    print("6. List all")
    print("7. Clear all")
    print("0. Back")
    return input("Option: ")

# Reuse existing functions: import/export/add/remove/list/clear and manage_employees()

# Sub-menu dispatchers

def user_management_menu():
    while True:
        print(f"\n{MAGENTA}--- USER MANAGEMENT ---{RESET}")
        print("1. Create user")
        print("2. Update user")
        print("3. Modify Gmail settings")
        print("4. Suspend user")
        print("5. Reactivate user")
        print("6. Delete user")
        print("7. Undelete user")
        print("8. Lookup user info & groups")
        print("0. Back")
        c = input("Option: ")
        if c == '1': create_user()
        elif c == '2': update_user()
        elif c == '3': modify_gmail_settings()
        elif c == '4': suspend_user()
        elif c == '5': reactivate_user()
        elif c == '6': delete_user()
        elif c == '7': undelete_user()
        elif c == '8': lookup_user_full_info()
        elif c == '0': break
        else: print("Invalid option.")


def group_management_menu():
    while True:
        print(f"\n{MAGENTA}--- GROUP MANAGEMENT ---{RESET}")
        print("1. Create group")
        print("2. Delete group")
        print("3. Add member to group")
        print("4. Remove member from group")
        print("5. List group members")
        print("0. Back")
        c = input("Option: ")
        if c == '1': create_group()
        elif c == '2': delete_group()
        elif c == '3': add_user_to_group()
        elif c == '4': remove_user_from_group()
        elif c == '5': list_group_members()
        elif c == '0': break
        else: print("Invalid option.")


def drive_management_menu():
    while True:
        print(f"\n{MAGENTA}--- DRIVE MANAGEMENT ---{RESET}")
        print("1. List user files")
        print("2. Transfer ownership")
        print("0. Back")
        c = input("Option: ")
        if c == '1': list_files()
        elif c == '2': transfer_ownership()
        elif c == '0': break
        else: print("Invalid option.")


def main():
    display_header()
    fetch_employees_from_gworkspace()
    while True:
        print("\n--- MAIN MENU ---")
        print("1. User Management")
        print("2. Group Management")
        print("3. Drive Management")
        print("4. Employee DB")
        print("0. Exit")
        choice = input("Option: ")
        if choice == '1': user_management_menu()
        elif choice == '2': group_management_menu()
        elif choice == '3': drive_management_menu()
        elif choice == '4':
            from_manage = employee_management_menu()
            # call manage_employees similar to before
            if from_manage: manage_employees()
        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
