import subprocess
import os
import re
from collections import namedtuple
import configparser
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
import login  # Import the login system


# Authentication Menu Before Running Main Program
def authentication_menu():
    while True:
        print("\n--- Welcome to the System ---")
        print("1. Sign Up")
        print("2. Login")
        print("3. Forgot Password")
        print("4. Exit")

        try:
            choice = input("Choose an option: ").strip()

            if choice == "1":
                login.sign_up()
            elif choice == "2":
                logged_in_user = login.login()
                if logged_in_user:
                    return logged_in_user  # Exit loop if login is successful
            elif choice == "3":
                login.forgot_password()
            elif choice == "4":
                print("Exiting...")
                exit()
            else:
                print("❌ Invalid choice! Please enter a number (1-4).")

        except Exception as e:
            print(f"❌ Error: {e}")


# Call the authentication function before launching the GUI
logged_in_user = authentication_menu()

print(f"\n✅ Welcome, {logged_in_user}! Running main application...\n")

# Now run the main application after successful login

# Hacker-style colors
BACKGROUND_COLOR = "#000000"  # Black
FOREGROUND_COLOR = "#00FF00"  # Green
ACCENT_COLOR = "#00FF00"  # Green
TEXT_COLOR = "#00FF00"  # Green


def get_windows_saved_ssids():
    """Returns a list of saved SSIDs in a Windows machine using netsh command"""
    try:
        output = subprocess.check_output("netsh wlan show profiles", shell=True).decode(errors="ignore")
        profiles = re.findall(r"All User Profile\s*:\s*(.*)", output)
        return [profile.strip() for profile in profiles]
    except subprocess.CalledProcessError:
        print("❌ Error: Failed to fetch SSIDs on Windows.")
        return []


def get_windows_saved_wifi_passwords():
    """Extracts saved Wi-Fi passwords in a Windows machine"""
    ssids = get_windows_saved_ssids()
    Profile = namedtuple("Profile", ["ssid", "ciphers", "key"])
    profiles = []

    for ssid in ssids:
        try:
            ssid_details = subprocess.check_output(f'netsh wlan show profile "{ssid}" key=clear', shell=True).decode(
                errors="ignore")
            ciphers = re.findall(r"Cipher\s*:\s*(.*)", ssid_details)
            key = re.findall(r"Key Content\s*:\s*(.*)", ssid_details)

            profile = Profile(
                ssid=ssid,
                ciphers="/".join(ciphers).strip() if ciphers else "Unknown",
                key=key[0].strip() if key else "None"
            )
            profiles.append(profile)
        except subprocess.CalledProcessError:
            print(f"❌ Error: Could not retrieve password for {ssid}.")

    return profiles


def get_linux_saved_wifi_passwords():
    """Extracts saved Wi-Fi passwords saved in a Linux machine"""
    network_connections_path = "/etc/NetworkManager/system-connections/"
    if not os.path.exists(network_connections_path):
        print("❌ Error: NetworkManager config directory not found.")
        return []

    fields = ["ssid", "auth-alg", "key-mgmt", "psk"]
    Profile = namedtuple("Profile", [f.replace("-", "_") for f in fields])
    profiles = []

    for file in os.listdir(network_connections_path):
        data = {k.replace("-", "_"): None for k in fields}
        config = configparser.ConfigParser()
        config.read(os.path.join(network_connections_path, file))
        for _, section in config.items():
            for k, v in section.items():
                if k in fields:
                    data[k.replace("-", "_")] = v
        profile = Profile(**data)
        profiles.append(profile)

    return profiles


def display_profiles(search_query=None):
    """Displays the Wi-Fi profiles in the GUI, optionally filtered by search_query"""
    for row in tree.get_children():
        tree.delete(row)

    if os.name == "nt":
        profiles = get_windows_saved_wifi_passwords()
    else:
        profiles = get_linux_saved_wifi_passwords()

    for profile in profiles:
        if search_query and search_query.lower() not in profile.ssid.lower():
            continue  # Skip profiles that don't match the search query
        tree.insert("", "end", values=(profile.ssid, profile.ciphers, profile.key))


def on_search():
    """Handles the search functionality"""
    search_query = search_entry.get()
    display_profiles(search_query)


# Create the main window
root = tk.Tk()
root.title("Wi-Fi Password Viewer")
root.configure(bg=BACKGROUND_COLOR)

# Set hacker-style font
hacker_font = tkFont.Font(family="Courier", size=12, weight="bold")

# Create a frame for the search bar
search_frame = ttk.Frame(root)
search_frame.pack(pady=10)

# Create a search bar
search_entry = ttk.Entry(search_frame, width=50, font=hacker_font)
search_entry.pack(side=tk.LEFT, padx=5)

# Create a search button
search_button = ttk.Button(search_frame, text="Search", command=on_search)
search_button.pack(side=tk.LEFT)

# Create a frame for the treeview
tree_frame = ttk.Frame(root)
tree_frame.pack(pady=10)

# Create a treeview to display the Wi-Fi profiles
columns = ("SSID", "Ciphers", "Password") if os.name == "nt" else ("SSID", "Auth Alg", "Key Mgmt", "PSK")

tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
tree.pack()

# Configure the style for the treeview
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview",
                background=BACKGROUND_COLOR,
                foreground=TEXT_COLOR,
                fieldbackground=BACKGROUND_COLOR,
                font=hacker_font)
style.map("Treeview",
          background=[("selected", ACCENT_COLOR)],
          foreground=[("selected", BACKGROUND_COLOR)])

# Set the column headings
for col in columns:
    tree.heading(col, text=col, anchor=tk.CENTER)

# Create a button to refresh the profiles
refresh_button = ttk.Button(root, text="Refresh", command=lambda: display_profiles())
refresh_button.pack(pady=10)

# Display the profiles initially
display_profiles()

# Start the main loop
root.mainloop()
