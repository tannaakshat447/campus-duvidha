import sqlite3
import os
import shutil
from datetime import datetime

def migrate():
    db_path = 'campus_solver.db'
    backup_path = f'campus_solver_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return

    print(f"Creating backup: {backup_path}")
    shutil.copy2(db_path, backup_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Category Mapping
    cat_map = {
        "Infrastructure": "Infrastructure/Maintenance",
        "Academic": "Academic issues",
        "Hostel & Mess": "Mess and food quality",
        "Anti-Ragging": "Anti ragging and safety",
        "Administration": "Other",
        "IT & Network": "Other",
        "Needs Manual Review": "Other"
    }

    # Department Mapping
    dept_map = {
        "Maintenance & Infrastructure Dept.": "Maintenance & Infrastructure Dept.",
        "Academic Affairs Office": "Academic Affairs Office",
        "Hostel Warden & Mess Committee": "Mess & Catering Committee",
        "Anti-Ragging Cell": "Anti-Ragging & Security Cell",
        "Registrar / Admin Office": "Dean of Student Welfare",
        "IT Services & Network Dept.": "Dean of Student Welfare",
        "Dean of Student Welfare": "Dean of Student Welfare"
    }

    print("Starting migration...")

    # 1. Update problems table
    print("   Updating 'problems' table categories...")
    for old, new in cat_map.items():
        cursor.execute("UPDATE problems SET category = ? WHERE category = ?", (new, old))
        print(f"     [OK] {old} -> {new} ({cursor.rowcount} rows)")

    print("   Updating 'problems' table departments...")
    for old, new in dept_map.items():
        cursor.execute("UPDATE problems SET department = ? WHERE department = ?", (new, old))
        print(f"     [OK] {old} -> {new} ({cursor.rowcount} rows)")

    # 2. Update agent_logs table
    print("   Updating AI agent logs...")
    for old, new in cat_map.items():
        cursor.execute("UPDATE agent_logs SET output_json = REPLACE(output_json, ?, ?) WHERE agent_name LIKE 'Classifier%'", (f'"{old}"', f'"{new}"'))
    
    for old, new in dept_map.items():
        cursor.execute("UPDATE agent_logs SET output_json = REPLACE(output_json, ?, ?) WHERE agent_name LIKE 'Router%'", (f'"{old}"', f'"{new}"'))

    conn.commit()
    conn.close()
    print("\nMigration complete. Please restart your server if it's running.")

if __name__ == "__main__":
    migrate()
