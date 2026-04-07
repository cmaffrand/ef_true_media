#Function That Finds files in a folder and subfolders containing a specific word in their name

import os
import shutil
from rate_player import rate_player

def find_files(src_folder, keyword):
    """Find all files in the selected folder and subfolders containing a specific word in their name. And store the path of the found files in a list."""
    found_files = []
    
    for root, dirs, files in os.walk(src_folder):
        # Print the current directory being processed
        #print(f"\nProcessing directory: {root}")
        for file in files:
            if keyword in file:
                #print(f"Found: {os.path.join(root, file)}")
                found_files.append(os.path.join(root, file))
    
    if not found_files:
        print(f"No files found containing the keyword '{keyword}' in their name.")
    
    return found_files
                
# Funciton that take the arguments from the command line and call the copy_files function
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Find files containing a specific keyword in their name.')
    parser.add_argument('src_folder', type=str, help='The source folder to search in')
    parser.add_argument('keyword', type=str, help='The keyword to search for in file names')
    
    args = parser.parse_args()
    
    files = find_files(args.src_folder, args.keyword)   
    
    # Copy Files to a new folder called "Found_Files"
    if files:
        dest_folder = os.path.join("outputs", args.keyword)
        os.makedirs(dest_folder, exist_ok=True)
        for file in files:
            shutil.copy(file, dest_folder)
        print(f"\nCopied {len(files)} files to '{dest_folder}'")