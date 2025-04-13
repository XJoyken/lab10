import psycopg2
import csv
from psycopg2 import sql

db_params = {
    'dbname': 'phonebook',
    'user': 'postgres',
    'password': 'reshetka3435684',
    'host': 'localhost',
    'port': '5432'
}

def connect_db():
    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def create_phonebook_table():
    conn = connect_db()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phonebook (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50),
                phone VARCHAR(20) UNIQUE NOT NULL
            );
        """)
        conn.commit()
        print("Table phonebook created or already exists.")
    except Exception as e:
        print(f"Table creation error: {e}")
    finally:
        cur.close()
        conn.close()

def insert_from_csv(file_path):
    conn = connect_db()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                cur.execute(
                    "INSERT INTO phonebook (first_name, last_name, phone) VALUES (%s, %s, %s) ON CONFLICT (phone) DO NOTHING",
                    (row[0], row[1], row[2])
                )
        conn.commit()
        print("Data from CSV loaded successfully.")
    except Exception as e:
        print(f"CSV loading error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def insert_from_console():
    conn = connect_db()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        first_name = input("Enter first name: ")
        last_name = input("Enter last name (or leave empty): ")
        phone = input("Enter phone number: ")
        cur.execute(
            "INSERT INTO phonebook (first_name, last_name, phone) VALUES (%s, %s, %s) ON CONFLICT (phone) DO NOTHING",
            (first_name, last_name if last_name else None, phone)
        )
        conn.commit()
        print("Data added successfully.")
    except Exception as e:
        print(f"Data insertion error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def update_phonebook():
    conn = connect_db()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        print("Update: 1 - first name, 2 - phone")
        choice = input("Choose (1 or 2): ")
        phone_id = input("Enter record ID to update: ")
        
        if choice == '1':
            new_name = input("Enter new first name: ")
            cur.execute(
                "UPDATE phonebook SET first_name = %s WHERE id = %s",
                (new_name, phone_id)
            )
        elif choice == '2':
            new_phone = input("Enter new phone: ")
            cur.execute(
                "UPDATE phonebook SET phone = %s WHERE id = %s",
                (new_phone, phone_id)
            )
        else:
            print("Invalid choice.")
            return
        
        if cur.rowcount == 0:
            print("Record with this ID not found.")
        else:
            conn.commit()
            print("Data updated successfully.")
    except Exception as e:
        print(f"Update error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def query_phonebook():
    conn = connect_db()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        print("Filters: 1 - by first name, 2 - by phone, 3 - all records")
        choice = input("Choose (1, 2, or 3): ")
        
        if choice == '1':
            name = input("Enter first name to search: ")
            cur.execute(
                "SELECT id, first_name, last_name, phone FROM phonebook WHERE first_name ILIKE %s",
                (f"%{name}%",)
            )
        elif choice == '2':
            phone = input("Enter phone to search: ")
            cur.execute(
                "SELECT id, first_name, last_name, phone FROM phonebook WHERE phone ILIKE %s",
                (f"%{phone}%",)
            )
        elif choice == '3':
            cur.execute("SELECT id, first_name, last_name, phone FROM phonebook")
        else:
            print("Invalid choice.")
            return
        
        rows = cur.fetchall()
        if not rows:
            print("No records found.")
        else:
            for row in rows:
                print(f"ID: {row[0]}, First Name: {row[1]}, Last Name: {row[2] or 'N/A'}, Phone: {row[3]}")
    except Exception as e:
        print(f"Query error: {e}")
    finally:
        cur.close()
        conn.close()

def delete_from_phonebook():
    conn = connect_db()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        print("Delete by: 1 - first name, 2 - phone")
        choice = input("Choose (1 or 2): ")
        
        if choice == '1':
            name = input("Enter first name to delete: ")
            cur.execute(
                "DELETE FROM phonebook WHERE first_name = %s",
                (name,)
            )
        elif choice == '2':
            phone = input("Enter phone to delete: ")
            cur.execute(
                "DELETE FROM phonebook WHERE phone = %s",
                (phone,)
            )
        else:
            print("Invalid choice.")
            return
        
        if cur.rowcount == 0:
            print("No records found.")
        else:
            conn.commit()
            print(f"Deleted records: {cur.rowcount}")
    except Exception as e:
        print(f"Deletion error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def main():
    create_phonebook_table()
    while True:
        print("\nPhoneBook Menu:")
        print("1. Add data from CSV")
        print("2. Add data via console")
        print("3. Update data")
        print("4. Query data")
        print("5. Delete data")
        print("6. Exit")
        choice = input("Choose action (1-6): ")
        
        if choice == '1':
            file_path = input("Enter CSV file path: ")
            insert_from_csv(file_path)
        elif choice == '2':
            insert_from_console()
        elif choice == '3':
            update_phonebook()
        elif choice == '4':
            query_phonebook()
        elif choice == '5':
            delete_from_phonebook()
        elif choice == '6':
            print("Exiting program.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()