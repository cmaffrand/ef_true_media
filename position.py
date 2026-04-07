import os
import tkinter as tk
from tkinter import filedialog
import sys
from pathlib import Path
from rate_player import rate_player

def show_help():
    """Display help information"""
    help_text = """
Usage: python position.py [folder_path] [card_txt_filename]

    """
    print(help_text)

def select_folder():
    """Select folder containing player files"""
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select folder containing player files")
    return folder_path

def select_csv_file():
    """Select CSV profile file"""
    root = tk.Tk()
    root.withdraw()
    csv_path = filedialog.askopenfilename(
        title="Select CSV profile file",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    return csv_path

def select_txt_file():
    """Select TXT file for player list"""
    root = tk.Tk()
    root.withdraw()
    txt_path = filedialog.askopenfilename(
        title="Select TXT file containing player list",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    return txt_path

def process_players(folder_path, csv_path=Path("player_profiles.csv")):
    """Process all player files in the selected folder"""
    results = []
    
    if not folder_path:
        print("No folder selected")
        return results
    
    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    except Exception as e:
        print(f"Error reading folder: {e}")
        return results
    
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        #print(f"Processing path: {file_path}")
        try:
            player_name, final_score, base_attr_score, card_bonus, skills_bonus, added_skills, biometric_bonus = rate_player(file_path=file_path, csv_path=csv_path)
            results.append((final_score, player_name, base_attr_score, card_bonus, skills_bonus, added_skills, biometric_bonus, filename))
            # Print in Green for processed files
            print(f"\033[92mProcessed: {filename} - {player_name}: {final_score:.1f} (Base: {base_attr_score:.1f}, Card Bonus: {card_bonus:.1f}, Skills Bonus: {skills_bonus:.1f}, Skills To Add: {added_skills:.1f}, Biometric Bonus: {biometric_bonus:.1f})\033[0m")
        except Exception as e:
            # Print in Red for errors
            print(f"\033[91mError processing {filename}: {e}\033[0m")
    
    return results

def position(folder_path, txt_path):
    """Compare a player in txt file in every profile from the profile folder."""
    # Pritn table header
    print(f"{'Pos':<50} {'Player Name':<25} {'Score':<10} [Score w/o Skills] {' ':2}")
    
    # Search all profile CSV files in the profile_folder
    file_path = os.path.join("./", txt_path)
    profile_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    for profile_file in profile_files:
        profile_path = os.path.join(folder_path, profile_file)
        #print(f"\nComparing players using profile: {profile_file}")
        #print(profile_path)
        try:
            player_name, final_score, base_attr_score, card_bonus, skills_bonus, added_skills, biometric_bonus = rate_player(file_path=file_path, csv_path=profile_path)
            #print(f"\033[92mProcessed: {txt_path} - {player_name}: {final_score:.1f} (Base: {base_attr_score:.1f}, Card Bonus: {card_bonus:.1f}, Skills Bonus: {skills_bonus:.1f}, Skills To Add: {added_skills:.1f}, Biometric Bonus: {biometric_bonus:.1f})\033[0m")
            if final_score - added_skills >= 60:
                color = "\033[92m"  # Green
            elif 59 <= final_score - added_skills < 60:
                color = "\033[94m"  # Blue
            elif 57 <= final_score - added_skills < 59:
                color = "\033[93m"  # Yellow
            else:
                color = "\033[91m"  # Red                
            print(f"{color}{profile_file:<50} {player_name:<25} {final_score:<10.1f} ({final_score-added_skills:<3.1f})\033[0m")
        except Exception as e:
            print(f"\033[91mError processing {txt_path} with profile {profile_path}: {e}\033[0m")
    
def args_handler():
    """Handle command line arguments"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return
    
    folder_path = None
    csv_path = None
    
    # Check command line arguments
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        if not os.path.isdir(folder_path):
            print(f"Error: '{folder_path}' is not a valid directory")
            return
    else:
        folder_path = select_folder()
    
    # Check for csv_path parameter
    if len(sys.argv) > 2:
        csv_path = Path(sys.argv[2])
    else:
        # Fall back to GUI file selection
        csv_file = select_txt_file()
        csv_path = Path(csv_file) if csv_file else Path("player_profiles.txt")
        
    return folder_path, csv_path
    
if __name__ == "__main__":
    """Main function to run the comparison"""
    folder_path, txt_path = args_handler()
    print(f"Using folder_path parameter: {folder_path}")
    print(f"Using txt_path parameter: {txt_path}")
    position(folder_path, txt_path)