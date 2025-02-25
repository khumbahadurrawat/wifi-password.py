import mysql.connector
import re
import bcrypt

# Database connection
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",  # Change this if using a different MySQL user
        password="",
        database="user_auth"
    )
    cursor = db.cursor()
except mysql.connector.Error as err:
    print(f"❌ Database Connection Error: {err}")
    exit()

# Create users table if not exists
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        gmail VARCHAR(100) NOT NULL UNIQUE,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL
    )
    """)
    db.commit()
except mysql.connector.Error as err:
    print(f"❌ Error creating table: {err}")

# Function to validate user input
def validate_input(first_name, last_name, gmail, username, password, confirm_password):
    if not all([first_name, last_name, gmail, username, password, confirm_password]):
        print("❌ Error: All fields are required.")
        return False

    if not (first_name[0].isupper() and last_name[0].isupper()):
        print("❌ Error: First Name and Last Name must start with a capital letter.")
        return False

    if not gmail.endswith("@gmail.com"):
        print("❌ Error: Email must be a valid Gmail address (@gmail.com).")
        return False

    if not re.match(r"^(?=.*[a-zA-Z])(?=.*[\W_])(?=.*[0-9]).{6,}$", username):
        print("❌ Error: Username must contain letters, numbers, and special characters.")
        return False

    cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        print("❌ Error: Username already exists. Choose a different one.")
        return False

    if len(password) < 8:
        print("❌ Error: Password must be at least 8 characters long.")
        return False

    if password != confirm_password:
        print("❌ Error: Password and Confirm Password do not match.")
        return False

    return True

# Function to hash password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Function to verify password
def verify_password(stored_password, entered_password):
    return bcrypt.checkpw(entered_password.encode('utf-8'), stored_password.encode('utf-8'))

# Sign Up Function
def sign_up():
    """Handles user registration."""
    print("\n--- Sign Up ---")
    first_name = input("Enter First Name (First letter must be capital): ").strip()
    last_name = input("Enter Last Name (First letter must be capital): ").strip()
    gmail = input("Enter Gmail (Must include '@gmail.com'): ").strip()
    username = input("Enter Username (Mix of letters, special characters, and numbers, unique): ").strip()

    # 🔥 FIX: Using input() instead of getpass.getpass() to avoid freezing
    password = input("Enter Password (At least 8 characters): ").strip()
    confirm_password = input("Confirm Password: ").strip()

    if validate_input(first_name, last_name, gmail, username, password, confirm_password):
        hashed_password = hash_password(password)
        try:
            cursor.execute("INSERT INTO users (first_name, last_name, gmail, username, password) VALUES (%s, %s, %s, %s, %s)",
                           (first_name, last_name, gmail, username, hashed_password))
            db.commit()
            print("✅ Sign Up Successful! You can now log in.")
        except mysql.connector.Error as err:
            print(f"❌ Database Error: {err}")

# Login Function
def login():
    """Handles user login and returns the username if successful."""
    print("\n--- Login ---")
    username = input("Enter Username: ").strip()
    password = input("Enter Password: ").strip()  # 🔥 FIX: Avoids `getpass.getpass()` freeze

    cursor.execute("SELECT password, first_name, last_name FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and verify_password(user[0], password):
        print(f"✅ Login Successful! Welcome, {user[1]} {user[2]}")
        return username  # Return the logged-in username
    else:
        print("❌ Error: Invalid Username or Password.")
        return None  # Return None if login fails

# Forgot Password Function
def forgot_password():
    """Handles the password reset process."""
    print("\n--- Forgot Password ---")
    username = input("Enter Username: ").strip()
    gmail = input("Enter Gmail: ").strip()

    cursor.execute("SELECT * FROM users WHERE username = %s AND gmail = %s", (username, gmail))
    user = cursor.fetchone()

    if user:
        new_password = input("Enter New Password (At least 8 characters): ").strip()
        confirm_password = input("Confirm New Password: ").strip()

        if len(new_password) < 8:
            print("❌ Error: Password must be at least 8 characters long.")
            return

        if new_password != confirm_password:
            print("❌ Error: Password and Confirm Password do not match.")
            return

        hashed_new_password = hash_password(new_password)
        cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_new_password, username))
        db.commit()
        print("✅ Password Reset Successful! You can now log in.")
    else:
        print("❌ Error: Username or Gmail is incorrect.")

# Main Menu (Only executes when run as main script)
if __name__ == "__main__":
    try:
        while True:
            print("\n--- Menu ---")
            print("1. Sign Up")
            print("2. Login")
            print("3. Forgot Password")
            print("4. Exit")

            choice = input("Choose an option: ")

            if choice == "1":
                sign_up()
            elif choice == "2":
                login()
            elif choice == "3":
                forgot_password()
            elif choice == "4":
                print("Exiting...")
                break
            else:
                print("❌ Invalid choice! Please try again.")

    finally:
        # Close database connection before exiting
        cursor.close()
        db.close()
