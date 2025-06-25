#!/usr/bin/env python3
"""
FIX Session Configuration Script
Automates adding FIX session configurations to a file
"""

import os
import getpass
import base64
from datetime import datetime

def encrypt_password(password):
    """Simple encryption using base64 encoding"""
    try:
        encoded_bytes = base64.b64encode(password.encode('utf-8'))
        return encoded_bytes.decode('utf-8')
    except Exception as e:
        print(f"Error encrypting password: {e}")
        return password

def get_user_input():
    """Get all required session parameters from user"""
    print("FIX Session Configuration Tool")
    print("-" * 30)
    
    sender_comp_id = input("Enter SenderCompID: ").strip()
    target_comp_id = input("Enter TargetCompID: ").strip()
    port = input("Enter Port: ").strip()
    ip = input("Enter IP Address: ").strip()
    username = input("Enter Username: ").strip()
    
    # Use getpass for secure password input (hidden from console)
    password = getpass.getpass("Enter Password: ").strip()
    
    if not all([sender_comp_id, target_comp_id, port, ip, username, password]):
        raise ValueError("All fields (SenderCompID, TargetCompID, Port, IP, Username, Password) are required")
    
    # Validate port is numeric
    try:
        int(port)
    except ValueError:
        raise ValueError("Port must be a valid number")
    
    # Encrypt password
    encrypted_password = encrypt_password(password)
    print("Password encrypted for storage.")
    
    return sender_comp_id, target_comp_id, port, ip, username, encrypted_password

def create_fix_session_config(sender_comp_id, target_comp_id, port, ip, username, encrypted_password):
    """Create FIX session configuration string"""
    session_config = f"""
# FIX Session Configuration - Added {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Note: Password is base64 encoded for basic protection
[SESSION]
BeginString=FIX.4.4
SenderCompID={sender_comp_id}
TargetCompID={target_comp_id}
SessionQualifier=
DefaultApplVerID=FIX50SP2
ConnectionType=initiator
StartTime=00:00:00
EndTime=23:59:59
HeartBtInt=30
SocketConnectPort={port}
SocketConnectHost={ip}
Username={username}
Password={encrypted_password}
FileStorePath=store
DataDictionary=FIX44.xml
ResetOnLogon=Y
ResetOnLogout=Y
ResetOnDisconnect=Y
"""
    return session_config

def add_to_file(config_content, filename="fix_sessions.cfg"):
    """Add configuration to file"""
    try:
        # Check if file exists and create backup
        if os.path.exists(filename):
            backup_name = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(filename, 'r') as original:
                with open(backup_name, 'w') as backup:
                    backup.write(original.read())
            print(f"Backup created: {backup_name}")
        
        # Append new configuration
        with open(filename, 'a') as f:
            f.write(config_content)
        
        print(f"FIX session configuration added to {filename}")
        
    except Exception as e:
        print(f"Error writing to file: {e}")
        return False
    
    return True

def display_preview(config_content):
    """Display configuration preview"""
    print("\nConfiguration Preview:")
    print("=" * 50)
    print(config_content)
    print("=" * 50)
    
    confirm = input("\nAdd this configuration? (y/n): ").strip().lower()
    return confirm in ['y', 'yes']

def main():
    """Main function"""
    try:
        # Get user input
        sender_comp_id, target_comp_id, port, ip, username, encrypted_password = get_user_input()
        
        # Create configuration
        config_content = create_fix_session_config(sender_comp_id, target_comp_id, port, ip, username, encrypted_password)
        
        # Show preview and get confirmation
        if display_preview(config_content):
            # Get filename (optional)
            filename = input("\nEnter filename (press Enter for 'fix_sessions.cfg'): ").strip()
            if not filename:
                filename = "fix_sessions.cfg"
            
            # Add to file it will not override the exsting fix session that is already in the file it adds it.
            if add_to_file(config_content, filename):
                print("\n✓ FIX session configuration successfully added!")
                print("Note: Password has been encrypted using base64 encoding.")
            else:
                print("\n✗ Failed to add configuration")
        else:
            print("\nConfiguration cancelled.")
            
    except ValueError as e:
        print(f"Input error: {e}")
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()