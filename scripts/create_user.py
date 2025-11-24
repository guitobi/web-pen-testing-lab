import sqlite3, getpass, os, sys

DB_PATH = "shop.db"

def main():
    if not os.path.exists(DB_PATH):
        print("DB not found. Start backend first.")
        sys.exit(1)

    username = input("Username: ")
    password = getpass.getpass("Password: ")
    role = input("Role (admin/user): ") or "user"

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    query = f"INSERT INTO users (username, password, role) VALUES ('{username}', '{password}', '{role}')"
    try:
        cur.execute(query)
        conn.commit()
        print("User created.")
    except Exception as e:
        print("Error:", e)
    conn.close()

if __name__ == "__main__":
    main()
