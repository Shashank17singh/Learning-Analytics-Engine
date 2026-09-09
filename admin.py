import sqlite3 as db

import auth_utils
import assessment_mgmt


def auth(conn):
    """Authenticate admin user with parameterized query to prevent SQL injection."""
    cur = conn.cursor()
    print("\n--- Admin Login ---")
    un = input("Enter username: ").strip().lower()
    pwd = input("Enter password: ").strip()

    pwd_hash = auth_utils.hash_password(pwd)
    cur.execute(
        "SELECT username, role FROM login WHERE LOWER(TRIM(username)) = ? AND TRIM(password) = ? AND status = 'active'",
        (un, pwd_hash),
    )
    rs = cur.fetchone()
    cur.close()

    if rs is None:
        print("\n[!] Invalid username or password.")
    else:
        role = rs[1] if rs else "admin"
        print(f"\n[+] Welcome {role} ({un})!")
        manageAdmin(conn, un)


def manageAdmin(conn, username):
    """Admin dashboard menu."""
    while True:
        try:
            choice = int(input("""
--- Admin Dashboard ---
1) Manage Assessment Questions
2) Create New Admin
3) Change Password
4) Logout
Enter your choice -> """).strip())
        except ValueError:
            print("\n[!] Invalid choice. Please enter a number (1-4).")
            continue

        if choice == 1:
            assessment_management_menu(conn)
        elif choice == 2:
            createNewAdmin(conn)
        elif choice == 3:
            changeAdminPassword(conn, username)
        elif choice == 4:
            print(f"Logged out from {username}.")
            break
        else:
            print("\n[!] Invalid choice. Please select from 1 to 4.")


def createNewAdmin(conn):
    """Create a new admin user safely with parameterized query."""
    cur = conn.cursor()
    print("\n--- Create New Admin ---")
    un = input("Enter new admin username: ").strip()
    if not un:
        print("[!] Username cannot be empty.")
        cur.close()
        return

    cur.execute("SELECT username FROM login WHERE username = ?", (un,))
    if cur.fetchone():
        print(f"[!] User '{un}' already exists.")
        cur.close()
        return

    pwd = input("Enter password: ").strip()
    confirmpwd = input("Confirm password: ").strip()

    if pwd == confirmpwd:
        pwd_hash = auth_utils.hash_password(pwd)
        cur.execute(
            "INSERT INTO login VALUES (?, ?, 'admin', 'active')", (un, pwd_hash)
        )
        conn.commit()
        print(f"[+] Admin '{un}' created successfully!")
    else:
        print("[!] Password mismatch. Admin not created.")
    cur.close()


def changeAdminPassword(conn, un):
    """Change admin password safely with parameterized query."""
    cur = conn.cursor()
    print(f"\n--- Change Password for '{un}' ---")
    newpwd = input("Enter new password: ").strip()
    confirmpwd = input("Confirm new password: ").strip()

    if not newpwd:
        print("[!] Password cannot be empty.")
        cur.close()
        return

    if newpwd == confirmpwd:
        pwd_hash = auth_utils.hash_password(newpwd)
        cur.execute("UPDATE login SET password = ? WHERE username = ?", (pwd_hash, un))
        conn.commit()
        print("[+] Password changed successfully!")
    else:
        print("[!] Password mismatch. Password not changed.")
    cur.close()


def assessment_management_menu(conn):
    """Assessment question management menu with View, Add, Update, Delete, and CSV Load."""
    while True:
        try:
            choice = int(input("""
--- Assessment Management ---
1) Load Questions from CSV
2) Add Question
3) View All Questions
4) Update Question
5) Delete Question
6) Back to Admin Menu
Enter your choice -> """).strip())
        except ValueError:
            print("\n[!] Invalid choice. Please enter a number (1-6).")
            continue

        if choice == 1:
            assessment_mgmt.loadQuestions(conn)
        elif choice == 2:
            assessment_mgmt.addQuestion(conn)
        elif choice == 3:
            assessment_mgmt.viewQuestions(conn)
        elif choice == 4:
            assessment_mgmt.updateQuestion(conn)
        elif choice == 5:
            assessment_mgmt.deleteQuestion(conn)
        elif choice == 6:
            break
        else:
            print("\n[!] Invalid choice. Please select from 1 to 6.")
