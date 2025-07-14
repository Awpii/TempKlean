#!/usr/bin/env python3

import os
import shutil
import stat
import sys
from pathlib import Path


class Colors:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def get_folder_size(folder_path):
    """Calculate the total size of a folder in bytes"""
    total_size = 0
    if not os.path.exists(folder_path):
        return 0
    
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                try:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
                except (OSError, IOError):
                    continue
    except (OSError, IOError):
        pass
    
    return total_size

def bytes_to_mb(bytes_size):
    """Convert bytes to megabytes with 2 decimal places"""
    return round(bytes_size / (1024 * 1024), 2)

def bytes_to_gb(bytes_size):
    """Convert bytes to gigabytes with 2 decimal places"""
    return round(bytes_size / (1024 * 1024 * 1024), 2)

def format_size(bytes_size):
    """Format bytes to the most appropriate unit"""
    if bytes_size >= 1024 * 1024 * 1024:
        return f"{bytes_to_gb(bytes_size):.2f} GB"
    else:
        return f"{bytes_to_mb(bytes_size):.2f} MB"

def create_progress_bar(percentage, width=30, filled_char='█', empty_char='░'):
    """Create a colorful progress bar"""
    filled_width = int(width * percentage / 100)
    empty_width = width - filled_width
    
    
    if percentage < 25:
        color = Colors.BRIGHT_GREEN
    elif percentage < 50:
        color = Colors.YELLOW
    elif percentage < 75:
        color = Colors.BRIGHT_YELLOW
    else:
        color = Colors.BRIGHT_RED
    
    bar = color + filled_char * filled_width + Colors.DIM + empty_char * empty_width + Colors.RESET
    return f"[{bar}] {percentage:.1f}%"

def get_disk_usage():
    """Get disk usage for the system drive"""
    try:
        import psutil
        disk_usage = psutil.disk_usage('C:')
        return disk_usage.total, disk_usage.used, disk_usage.free
    except ImportError:
        print(f"{Colors.YELLOW}Note: psutil not installed, skipping disk usage display{Colors.RESET}")
        return 0, 0, 0
    except:
        return 0, 0, 0

def display_system_info():
    """Display system information similar to neofetch"""
    print(f"{Colors.BRIGHT_CYAN}╭─────────────────────────────────────────╮{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}│{Colors.BRIGHT_YELLOW}     🧹 TEMP FILES CLEANUP TOOL 🧹     {Colors.BRIGHT_CYAN}│{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}╰─────────────────────────────────────────╯{Colors.RESET}")
    print()
    
    
    total_disk, used_disk, free_disk = get_disk_usage()
    
    if total_disk > 0:
        used_percentage = (used_disk / total_disk) * 100
        print(f"{Colors.BRIGHT_WHITE}System Drive Usage:{Colors.RESET}")
        print(f"  {create_progress_bar(used_percentage)}")
        print(f"  {Colors.BRIGHT_BLUE}Used:{Colors.RESET} {format_size(used_disk)} / {format_size(total_disk)}")
        print(f"  {Colors.BRIGHT_GREEN}Free:{Colors.RESET} {format_size(free_disk)}")
        print()

def handle_remove_readonly(func, path, exc):
    """Handle read-only files during deletion"""
    if os.path.exists(path):
        os.chmod(path, stat.S_IWRITE)
        func(path)

def clean_temp_folder(folder_path, location_name):
    """Clean a temporary folder and return the amount of space freed"""
    if not os.path.exists(folder_path):
        print(f"{Colors.BRIGHT_RED}Path not found: {folder_path}{Colors.RESET}")
        return 0
    
    print(f"{Colors.BRIGHT_YELLOW}🔄 Cleaning {location_name}...{Colors.RESET}")
    
    initial_size = get_folder_size(folder_path)
    files_deleted = 0
    folders_deleted = 0
    errors = 0
    
    try:
        items = list(Path(folder_path).iterdir())
        
        for item in items:
            try:
                if item.is_file():
                    item.unlink()
                    files_deleted += 1
                elif item.is_dir():
                    shutil.rmtree(str(item), onerror=handle_remove_readonly)
                    folders_deleted += 1
            except (OSError, IOError, PermissionError) as e:
                print(f"  {Colors.YELLOW}⚠️  Skipped: {item.name} (in use or protected){Colors.RESET}")
                errors += 1
                continue
    
    except Exception as e:
        print(f"{Colors.BRIGHT_RED}❌ Error accessing {location_name}: {e}{Colors.RESET}")
        return 0
    
    final_size = get_folder_size(folder_path)
    space_freed = initial_size - final_size
    
    print(f"  {Colors.BRIGHT_GREEN}✅ Files deleted: {files_deleted}{Colors.RESET}")
    print(f"  {Colors.BRIGHT_GREEN}✅ Folders deleted: {folders_deleted}{Colors.RESET}")
    if errors > 0:
        print(f"  {Colors.YELLOW}⚠️  Items skipped: {errors}{Colors.RESET}")
    
    return space_freed

def display_cleanup_results(user_temp_freed, system_temp_freed, user_temp_initial, system_temp_initial):
    """Display cleanup results with visual graphs"""
    total_freed = user_temp_freed + system_temp_freed
    total_initial = user_temp_initial + system_temp_initial
    
    print(f"\n{Colors.BRIGHT_CYAN}╭─────────────────────────────────────────╮{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}│{Colors.BRIGHT_YELLOW}            CLEANUP RESULTS              {Colors.BRIGHT_CYAN}│{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}╰─────────────────────────────────────────╯{Colors.RESET}")
    print()
    
    
    user_percentage = (user_temp_freed / user_temp_initial * 100) if user_temp_initial > 0 else 0
    print(f"{Colors.BRIGHT_WHITE}User Temp Folder:{Colors.RESET}")
    print(f"  {create_progress_bar(user_percentage)}")
    print(f"  {Colors.BRIGHT_GREEN}Recovered:{Colors.RESET} {format_size(user_temp_freed)}")
    print()
    
    
    system_percentage = (system_temp_freed / system_temp_initial * 100) if system_temp_initial > 0 else 0
    print(f"{Colors.BRIGHT_WHITE}System Temp Folder:{Colors.RESET}")
    print(f"  {create_progress_bar(system_percentage)}")
    print(f"  {Colors.BRIGHT_GREEN}Recovered:{Colors.RESET} {format_size(system_temp_freed)}")
    print()
    
    
    total_percentage = (total_freed / total_initial * 100) if total_initial > 0 else 0
    print(f"{Colors.BRIGHT_WHITE}Total Cleanup:{Colors.RESET}")
    print(f"  {create_progress_bar(total_percentage, width=40)}")
    print(f"  {Colors.BRIGHT_MAGENTA}💾 TOTAL SPACE RECOVERED: {format_size(total_freed)}{Colors.RESET}")
    print()
    
    
    print(f"{Colors.BRIGHT_CYAN}📊 Summary:{Colors.RESET}")
    print(f"  {Colors.BRIGHT_GREEN}🗂️  Total files/folders processed{Colors.RESET}")
    print(f"  {Colors.BRIGHT_YELLOW}⚡ Cleanup efficiency: {total_percentage:.1f}%{Colors.RESET}")
    print(f"  {Colors.BRIGHT_BLUE}💽 Space optimization complete{Colors.RESET}")

def main():
    try:
        
        if os.name == 'nt':
            os.system('color')
        
        display_system_info()
        
        print(f"{Colors.BRIGHT_YELLOW}🔍 Starting cleanup process...{Colors.RESET}\n")
        
        
        user_temp_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp')
        system_temp_path = r'C:\Windows\Temp'
        
        print(f"Debug: User temp path: {user_temp_path}")
        print(f"Debug: System temp path: {system_temp_path}")
        
        
        print(f"{Colors.BRIGHT_CYAN}📏 Calculating initial folder sizes...{Colors.RESET}")
        user_temp_initial_size = get_folder_size(user_temp_path)
        system_temp_initial_size = get_folder_size(system_temp_path)
        
        print(f"\n{Colors.BRIGHT_WHITE}Initial sizes:{Colors.RESET}")
        print(f"  {Colors.CYAN}User Temp:{Colors.RESET} {format_size(user_temp_initial_size)}")
        print(f"  {Colors.CYAN}System Temp:{Colors.RESET} {format_size(system_temp_initial_size)}")
        print()
        
        
        user_temp_freed = clean_temp_folder(user_temp_path, "User Temp folder")
        print()
        
        
        system_temp_freed = clean_temp_folder(system_temp_path, "System Temp folder")
        
        
        display_cleanup_results(user_temp_freed, system_temp_freed, user_temp_initial_size, system_temp_initial_size)
        
        print(f"\n{Colors.BRIGHT_GREEN}✨ Cleanup completed successfully!{Colors.RESET}")
        print(f"{Colors.DIM}Note: Some files may have been skipped if they were in use by running programs.{Colors.RESET}")
        print()
        
    except Exception as e:
        print(f"{Colors.BRIGHT_RED}❌ An unexpected error occurred: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
    
    finally:
       
        print(f"{Colors.BRIGHT_CYAN}Press Enter to exit...{Colors.RESET}")
        try:
            input()
        except:
            
            import msvcrt
            print("Press any key to exit...")
            msvcrt.getch()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.BRIGHT_RED}❌ Operation cancelled by user.{Colors.RESET}")
        print("Press Enter to exit...")
        try:
            input()
        except:
            pass
    except Exception as e:
        print(f"{Colors.BRIGHT_RED}❌ Critical error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        print("Press Enter to exit...")
        try:
            input()
        except:
            pass
