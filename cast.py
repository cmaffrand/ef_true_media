
import os
import shutil
from pathlib import Path
from rate_player import rate_player

def position(folder_path, txt_path):
    """Compare a player in txt file in every profile from the profile folder."""    
    # Search all profile CSV files in the profile_folder
    file_path = os.path.join("./", txt_path)
    profile_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    Near59 = 0
    Near57 = 0
    
    for profile_file in profile_files:
        profile_path = os.path.join(folder_path, profile_file)
        #print(f"\nComparing players using profile: {profile_file}")
        #print(profile_path)
        try:
            player_name, final_score, base_attr_score, card_bonus, skills_bonus, added_skills, biometric_bonus = rate_player(file_path=file_path, csv_path=profile_path)
            if final_score - added_skills >= 60:
                return True, 0, 0
            elif 59 <= final_score - added_skills < 60:
                Near59 += 1
            elif 57 <= final_score - added_skills < 59:
                Near57 += 1                
        except Exception as e:
            print(f"\033[91mError processing {txt_path} with profile {profile_path}: {e}\033[0m")
            
    return False, Near59, Near57

# Procces all players 
def cast_players(src_folder, profile_folder):
    """Cast all players in the selected folder."""
    
    for root, dirs, files in os.walk(src_folder):
        # Print the current directory being processed
        print(f"\nProcessing directory: {root}")
        for file in files:
            src_file = os.path.join(root, file)
            if file.endswith('.txt'):
                try:
                    is_casted, near59, near57 = position(profile_folder, src_file)
                    if is_casted:
                        pass
                    else:
                        if near59 > 0:
                            color = "\033[95m"  # Violet
                        elif near57 > 0:
                            color = "\033[93m"  # Yellow
                        else:
                            color = "\033[91m"  # Red
                            
                        print(f"{color}Not Casted: {src_file} (Near 59: {near59}, Near 57: {near57})\033[0m")
                except Exception as e:
                    print(f"\033[91mError processing {src_file}: {e}\033[0m")                   

            
# Funciton that take the arguments from the command line and call the copy_files function
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python3 cast.py <src_folder> <profile_folder>")
        sys.exit(1)
    
    src_folder = sys.argv[1]
    profile_folder = sys.argv[2]
        
    cast_players(src_folder, profile_folder)