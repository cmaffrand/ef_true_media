import os
import tkinter as tk
from tkinter import filedialog
import sys
from pathlib import Path
from rate_player import rate_player

def show_help():
    """Display help information"""
    help_text = """
Usage: python3 compare.py [folder_path] [csv_path] [options]

Arguments:
    folder_path    Path to folder containing player files (optional - GUI will open if not provided)
    csv_path       Path to CSV profile file (optional - GUI will open if not provided)

Options:
    -h, --help     Show this help message and exit

Examples:
    python3 compare.py
    python3 compare.py /path/to/players
    python3 compare.py /path/to/players custom_profiles.csv
    python3 compare.py --help
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

def compare(folder_path, csv_path=Path("player_profiles.csv")):
    """Compare players in the selected folder and print rankings"""
    #print(f"Using folder_path parameter: {folder_path}")
    #print(f"Using csv_path parameter: {csv_path}")
    
    results = process_players(folder_path, csv_path)
    results.sort(key=lambda x: x[0], reverse=True)
    
    epic=0
    showtime=0
    destacado=0
    pow=0
    normal=0
    
    table_width = 140
    
    print("\n" + "="*table_width)
    csv_path = Path(csv_path)
    print(f"FINAL RANKINGS for profile: {csv_path.name} (Sorted by Score)")
    print("="*table_width)
    print(f"{'Rank':<2} {'Type':<2} {'Player Name':<25} {'Total':<14} {'Stats':<10} {'Card':<10} {'Skills (ToAdd)':<15} {'Bio':<5} {'File Name':<20}")
    print("-"*table_width)
    
    for i, (score, player_name, base_attr_score, card_bonus, skills_bonus, added_skills, biometric_bonus, filename) in enumerate(results, 1):
        # if file name starts with Epic, print in Green, if starts with BigTime in yellow, Destacado in cyan, POW in violet, ShowTime is orange, Legendary in pink
        if filename.lower().startswith("epic"):
            epic += 1
            print(f"\033[92m{i:<4} {epic:<4} {player_name:<25} {score:<0.1f} ({score-added_skills:<3.1f}) {' ':2.0} {base_attr_score:<10.1f} {card_bonus:<10.1f} {skills_bonus:<6.1f} ({added_skills:<0.1f}) {' ':2.0} {biometric_bonus:<5.1f} {filename:<20}\033[0m")
        elif filename.lower().startswith("bigtime"):
            epic += 1
            print(f"\033[94m{i:<4} {epic:<4} {player_name:<25} {score:<0.1f} ({score-added_skills:<3.1f}) {' ':2.0} {base_attr_score:<10.1f} {card_bonus:<10.1f} {skills_bonus:<6.1f} ({added_skills:<0.1f}) {' ':2.0} {biometric_bonus:<5.1f} {filename:<20}\033[0m")
        elif filename.lower().startswith("destacado"):
            destacado += 1
            print(f"\033[96m{i:<4} {destacado:<4} {player_name:<25} {score:<0.1f} ({score-added_skills:<3.1f}) {' ':2.0} {base_attr_score:<10.1f} {card_bonus:<10.1f} {skills_bonus:<6.1f} ({added_skills:<0.1f}) {' ':2.0} {biometric_bonus:<5.1f} {filename:<20}\033[0m")
        elif filename.lower().startswith("pow"):
            pow += 1
            print(f"\033[95m{i:<4} {pow:<4} {player_name:<25} {score:<0.1f} ({score-added_skills:<3.1f}) {' ':2.0} {base_attr_score:<10.1f} {card_bonus:<10.1f} {skills_bonus:<6.1f} ({added_skills:<0.1f}) {' ':2.0} {biometric_bonus:<5.1f} {filename:<20}\033[0m")
        elif filename.lower().startswith("showtime"):
            showtime += 1
            print(f"\033[33m{i:<4} {showtime:<4} {player_name:<25} {score:<0.1f} ({score-added_skills:<3.1f}) {' ':2.0} {base_attr_score:<10.1f} {card_bonus:<10.1f} {skills_bonus:<6.1f} ({added_skills:<0.1f}) {' ':2.0} {biometric_bonus:<5.1f} {filename:<20}\033[0m")
        elif filename.lower().startswith("legendary"):
            epic += 1
            print(f"\033[93m{i:<4} {epic:<4} {player_name:<25} {score:<0.1f} ({score-added_skills:<3.1f}) {' ':2.0} {base_attr_score:<10.1f} {card_bonus:<10.1f} {skills_bonus:<6.1f} ({added_skills:<0.1f}) {' ':2.0} {biometric_bonus:<5.1f} {filename:<20}\033[0m")
        else:
            normal += 1
            print(f"{i:<4} {normal:<4} {player_name:<25} {score:<0.1f} ({score-added_skills:<3.1f}) {' ':2.0} {base_attr_score:<10.1f} {card_bonus:<10.1f} {skills_bonus:<6.1f} ({added_skills:<0.1f}) {' ':2.0} {biometric_bonus:<5.1f} {filename:<20}")        
    print("="*table_width + "\n")
    
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
        csv_file = select_csv_file()
        csv_path = Path(csv_file) if csv_file else Path("player_profiles.csv")
        
    return folder_path, csv_path
    
if __name__ == "__main__":
    """Main function to run the comparison"""
    folder_path, csv_path = args_handler()
    print(f"Using folder_path parameter: {folder_path}")
    print(f"Using csv_path parameter: {csv_path}")
    compare(folder_path, csv_path)