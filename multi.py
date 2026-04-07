import os
from pathlib import Path
import sys
from compare import compare, select_folder

def multi(players_folder, profile_folder):
    """
    Compare all players in every profile from the profile folder.
    
    Args:
        players_folder: Path to the folder containing player files
        profile_folder: Path to the folder containing profile folders
    """
    # Search all profile CSV files in the profile_folder
    profile_files = [f for f in os.listdir(profile_folder) if f.endswith('.csv')]
    for profile_file in profile_files:
        profile_path = os.path.join(profile_folder, profile_file)
        #print(f"\nComparing players using profile: {profile_file}")
        #print(players_folder)
        #print(profile_path)
        compare(players_folder, profile_path)
                    
def show_help():
    """Display help information for multi.py"""
    help_text = """
    Usage: python3 multi.py [players_folder] [profile_folder]
    Arguments:
        players_folder    Path to folder containing player files
        profile_folder    Path to folder containing profile folders
    Examples:
        python3 multi.py /path/to/players /path/to/profiles
    """
    print(help_text)    
                    
def args_handler():
    """Handle command line arguments"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return
    
    players_path = None
    profile_path = None
    
    # Check command line arguments
    if len(sys.argv) > 1:
        players_path = sys.argv[1]
        if not os.path.isdir(players_path):
            print(f"Error: '{players_path}' is not a valid directory")
            return
    else:
        players_path = select_folder()
    
    # Check for profile_path parameter
    if len(sys.argv) > 2:
        profile_path = Path(sys.argv[2])
        if not os.path.isdir(profile_path):
            print(f"Error: '{profile_path}' is not a valid directory")
            return
    else:
        profile_path = select_folder()
        
    return players_path, profile_path

if __name__ == "__main__":
    args = args_handler()
    if args:
        players_folder, profile_folder = args
        multi(players_folder, profile_folder)                    