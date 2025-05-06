import psutil
import os
import time
import subprocess
import sys

def get_top_memory_processes(num_processes=5):
    """
    Retrieves the top processes based on memory usage.

    Args:
        num_processes (int, optional): The number of top processes to retrieve. Defaults to 5.

    Returns:
        list: A list of tuples, where each tuple contains:
            - The process ID (PID)
            - The process name
            - The memory usage as a percentage
            - The memory usage in bytes
            - The username of the process owner
        Returns an empty list on error.
    """
    try:
        # Get a list of all running processes.
        processes = psutil.process_iter()
    except Exception as e:
        print(f"Error getting process list: {e}")
        return []

    # Sort processes by memory usage.
    process_memory = []
    for p in processes:
        try:
            # Get the memory_percent and memory_info in one call to reduce overhead.
            mem_info = p.memory_full_info()
            mem_percent = p.memory_percent()
            username = p.username()  # Get the username
            process_memory.append((p.pid, p.name(), mem_percent, mem_info.rss, username))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Handle the case where a process disappears during iteration.
            pass
        except Exception as e:
            print(f"Error getting memory info for process {p.pid}: {e}")

    # Sort the processes by memory usage (highest first).
    process_memory = sorted(process_memory, key=lambda x: x[2], reverse=True)
    return process_memory[:num_processes]  # Return the top N processes

def get_process_disk_usage(pid):
    """
    Retrieves the disk usage (read and write) for a given process.

    Args:
        pid (int): The process ID.

    Returns:
        tuple: A tuple containing:
            - read_bytes (int): The number of bytes read by the process.
            - write_bytes (int): The number of bytes written by the process.
        Returns (0, 0) on error.
    """
    try:
        process = psutil.Process(pid)
        io_counters = process.io_counters()
        read_bytes = io_counters.read_bytes
        write_bytes = io_counters.write_bytes
        return read_bytes, write_bytes
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0, 0
    except Exception as e:
        print(f"Error getting disk usage for process {pid}: {e}")
        return 0, 0

def get_top_disk_files(num_files=5):
    """
    Retrieves the top files based on disk usage (size).  This version uses a more robust approach
    that should work on most Unix-like systems and Windows.  It avoids the problems with
    `os.listdir` and `os.path.getsize` when dealing with very large directories or files.

    Args:
        num_files (int, optional): The number of top files to retrieve. Defaults to 5.

    Returns:
        list: A list of tuples, where each tuple contains:
            - The file path
            - The file size in bytes
        Returns an empty list on error.
    """
    try:
        # Use a shell command to find the largest files.  This is more efficient
        # than iterating through all files in Python, especially on large systems.
        if os.name == 'nt':
            # Windows:  Use 'forfiles' command.
            command = f'forfiles /P "C:\\" /M "*" /c "cmd /c if @fsize gtr 0 echo @file @fsize" | sort /r /n | head -n {num_files}'
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            lines = result.stdout.strip().splitlines()
            files_and_sizes = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        file_path = parts[0]
                        file_size = int(parts[1])
                        files_and_sizes.append((file_path, file_size))
                    except ValueError:
                        print(f"Skipping invalid line: {line}")

        else:
            # Unix/Linux: Use 'find' and 'du' commands.
            command = f'find / -type f -print0 | xargs -0 du -b | sort -nr | head -n {num_files}'
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            lines = result.stdout.strip().splitlines()
            files_and_sizes = []
            for line in lines:
                parts = line.split()
                if len(parts) == 2:
                    try:
                        file_size = int(parts[0])
                        file_path = parts[1]
                        files_and_sizes.append((file_path, file_size))
                    except ValueError:
                         print(f"Skipping invalid line: {line}")
        return files_and_sizes

    except Exception as e:
        print(f"Error getting top disk files: {e}")
        return []



def display_top_memory_processes(top_processes):
    """
    Displays the top memory-consuming processes.

    Args:
        top_processes (list): A list of tuples, as returned by get_top_memory_processes().
    """
    if not top_processes:
        print("No processes found or error retrieving process information.")
        return

    print("\nTop 5 Memory-Consuming Processes:")
    print("--------------------------------------------------------------------------------------------------")
    print(f"{'PID':<6} {'User':<10} {'Name':<20} {'Memory %':<10} {'Memory (MB)':<12} {'Disk Read (MB)':<15} {'Disk Write (MB)':<15}")
    print("--------------------------------------------------------------------------------------------------")

    for pid, name, memory_percent, memory_bytes, username in top_processes:
        memory_mb = memory_bytes / (1024 * 1024)
        read_bytes, write_bytes = get_process_disk_usage(pid)
        read_mb = read_bytes / (1024 * 1024)
        write_mb = write_bytes / (1024 * 1024)
        if memory_percent >= 100:
            print(f"\033[1;31m{pid:<6} {username:<10} {name:<20} {memory_percent:<10.1f} {memory_mb:<12.1f} {read_mb:<15.1f} {write_mb:<15.1f} (100% Memory!)\033[0m")
        else:
            print(f"{pid:<6} {username:<10} {name:<20} {memory_percent:<10.1f} {memory_mb:<12.1f} {read_mb:<15.1f} {write_mb:<15.1f}")

    print("--------------------------------------------------------------------------------------------------")



def display_top_disk_files(top_files):
    """
    Displays the top files based on disk usage.

    Args:
        top_files (list): A list of tuples, as returned by get_top_disk_files().
    """
    if not top_files:
        print("\nNo files found or error retrieving file information.")
        return

    print("\nTop 5 Largest Files:")
    print("----------------------------------------------------------------------------------------")
    print(f"{'File Path':<40} {'Size (MB)':<12}")
    print("----------------------------------------------------------------------------------------")
    for file_path, file_size in top_files:
        size_mb = file_size / (1024 * 1024)
        print(f"{file_path:<40} {size_mb:<12.1f}")
    print("----------------------------------------------------------------------------------------")



def main():
    """
    Main function to run the script.
    """
    top_memory_processes = get_top_memory_processes()
    display_top_memory_processes(top_memory_processes)
    top_disk_files = get_top_disk_files()
    display_top_disk_files(top_disk_files)



if __name__ == "__main__":
    main()