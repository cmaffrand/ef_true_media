# ef_true_media
This repository contains an algorithm used to rank cards in eFootball.

# Usage

## Rate card script (rate_player.py)

- Player Rating System

    Usage: python3 rate_player.py [OPTIONS] <player_file> [csv_profile]

    Arguments:
        player_file       Path to the player text file to rate
        csv_profile       Path to CSV profile (default: player_profiles.csv)

    Options:
        -h, --h, -help, --help    Show this help message and exit

    Examples:
        python3 rate_player.py player.txt
        python3 rate_player.py player.txt custom_profile.csv
        python3 rate_player.py -h

## Compare cards script (compare.py)

- Card Comparison System

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

## Multiple cards comparison script (multi.py)

- Compare all players in every profile from the profile folder.

    Usage: python3 multi.py [players_folder] [profile_folder]
    Arguments:
        players_folder    Path to folder containing player files
        profile_folder    Path to folder containing profile folders
    Examples:
        python3 multi.py /path/to/players /path/to/profiles

## Rate card in multiple profiles script (position.py)

- Compare a player in txt file in every profile from the profile folder.

    Usage: python3 position.py [folder_path] [card_txt_filename]

## Find players with specific Name script (find.py)

- Find players with specific name in the player folder.

    Usage: python3 find.py [folder_path] [name_to_find]

## Perform a minimun rate find for cards in a folder script (cast.py)

- Cast all players in the selected folder.

    Usage: python3 cast.py <src_folder> <profile_folder>

## Parse HTML form efhub script (parse.py)

- Parse HTML form efhub and create player txt files.

    -- First Train the card in efhub
    -- then open the card page and save it as HTML. 
    -- Put the HTML file in a folder and run the script with the folder path and the type of card (e.g. "GP", "POW", "Epic", "BigTime", "Legend", "ShowTime", "Highlight")

    Usage: python3 parse.py <html_folder> <type_card_prefix>