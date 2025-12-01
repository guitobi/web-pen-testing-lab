import sqlite3
import os
from app.db import REAL_PRODUCT_TABLE, DB_PATH

print(f"📂 Checking DB at: {DB_PATH}")

if not os.path.exists(DB_PATH):
    print("❌ Error: shop.db file not found! Run the server to create it.")
    exit()

try:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    # 1. Перевірка таблиць
    print("🔍 Tables in DB:")
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    table_names = [t[0] for t in tables]
    print(table_names)
    
    if REAL_PRODUCT_TABLE not in table_names:
        print(f"❌ CRITICAL: Hidden table '{REAL_PRODUCT_TABLE}' is MISSING!")
    else:
        print(f"✅ Hidden table '{REAL_PRODUCT_TABLE}' exists.")
        
        # 2. Перевірка товарів
        count = cur.execute(f"SELECT count(*) FROM {REAL_PRODUCT_TABLE}").fetchone()[0]
        print(f"📊 Products count: {count}")
        
        if count == 0:
            print("❌ Table exists but is EMPTY. init_db() failed to populate data.")
        else:
            print("✅ Data seems fine. Issue might be in products.py")

    conn.close()

except Exception as e:
    print(f"❌ Database Error: {e}")