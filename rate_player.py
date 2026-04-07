import csv
import sys
import re
from pathlib import Path

STATS_LABELS = [
    "Offensive Awareness", "Ball Control", "Dribbling", "Tight Possession",
    "Low Pass", "Lofted Pass", "Finishing", "Heading", "Place Kicking", "Curl",
    "Defensive Awareness", "Defensive Engagement", "Tackling", "Aggression",
    "Goalkeeping", "Gk Catching", "GK Parrying", "GK Reflexes", "GK Reach",
    "Speed", "Acceleration", "Kicking Power", "Jump", "Physical Contact",
    "Balance", "Stamina", "Weak Foot Usage", "Weak Foot Acc", "Form",
    "Injury Resistance"
]

SKILL_LABELS = [
    "Long Range Curler", "Through Passing", "First Time Shot", "One Touch Pass",
    "Super Sub", "Interception", "Blocker", "Man Marking", "Double Touch", 
    "Long Range Shooting", "Aerial Superiority", "Sliding Tackle", 
    "Acrobatic Clearance", "Fighting Spirit", "Gamesmanship", "Weighted Pass", 
    "Outside Curler", "Cut Behind & Turn", "Low Lofted Pass", "Pinpoint Crossing", 
    "Chip Shot Control", "Heading", "Dipping Shot", "Rising Shots", "Sole Control", 
    "Flip Flap", "Heel Trick", "Scissors Feint", "Track Back", "Knuckle Shot", 
    "Rabona", "Acrobatic Finishing", "Captaincy", "Long Throw", "Penalty Specialist", 
    "Scotch Move", "Chop Turn", "Marseille Turn", "Sombrero", "No Look Pass", 
    "GK Low Punt", "GK Penalty Saver", "GK Long Throw", "GK High Punt"
]

PREMIUM_SKILL_LABELS = [
    "Phenomenal Finishing", "Long Reach Tackle", "Edged Crossing", "Bullet Header", 
    "Momentum Dribbling", "Visionary Pass", "Phenomenal Pass", "Blitz Curler", 
    "GK Directing Defence", "GK Spirit Roar", "Low Screamer", "Aerial Fort", 
    "Fortress", "Will Power", "Acceleration Burst", "Game Changing Pass", "Magnetic Feet"
]

BIOMETRICS_LABELS = [
    "Leg Length", "Arm Length", "Waist Size", "Chest", "Shoulder Width", "Neck Length"
]

def clean_text_keep_space_and_newline(s: str) -> str:
    # Keep letters, digits, spaces and newlines. Replace other chars with space.
    return ''.join(ch if (ch.isalnum() or ch.isspace()) else ' ' for ch in s)

def get_line(lines, n):
    # 1-based line index, counting empty lines.
    if 1 <= n <= len(lines):
        return lines[n-1].strip()
    return ""

def build_label_pattern(label: str) -> str:
    # Build a regex that allows flexible whitespace between words of the label and captures a number
    parts = label.split()
    esc_parts = [re.escape(p) for p in parts]
    # allow any whitespace (spaces/newlines) between words
    label_pat = r'\s+'.join(esc_parts)
    # match label as a whole word sequence, then optional colon/spaces/newlines, then a number (1-3 digits)
    pat = r'(?i)\b' + label_pat + r'\b\s*[:\-\s]*?(\d{1,3})\b'
    return pat

def find_stat(cleaned_text, label):
    pat = build_label_pattern(label)
    m = re.search(pat, cleaned_text, flags=re.IGNORECASE)
    if m:
        try:
            return int(m.group(1))
        except:
            return None
    # Try a fallback: number may appear on the next line after a label line like "Label\n 87"
    # We'll search for label alone then up to 40 chars then a number
    fallback = build_label_pattern(label).replace(r'\b\s*[:\-\s]*?(\d{1,3})\b', r'\b(?:.*?)(\d{1,3})\b')
    m2 = re.search(fallback, cleaned_text, flags=re.IGNORECASE | re.DOTALL)
    if m2:
        try:
            return int(m2.group(1))
        except:
            return None
    return None

def find_skill(cleaned_text, skill):
    pat = build_label_pattern(skill)
    m = re.search(pat, cleaned_text, flags=re.IGNORECASE)
    if m:
        return True
    return False

def parse_file(path: Path):
    txt = path.read_text(encoding='utf-8', errors='ignore')
    cleaned = clean_text_keep_space_and_newline(txt)
    # If Goalkeeping appears in the first 25 lines replace it with an empty line
    first_25_lines = cleaned.splitlines()[:25]
    if any("Goalkeeping" in line for line in first_25_lines):
        cleaned_lines = cleaned.splitlines()
        for i in range(min(25, len(cleaned_lines))):
            if "Goalkeeping" in cleaned_lines[i]:
                cleaned_lines[i] = ""
        cleaned = "\n".join(cleaned_lines)
    # Remove First Dribbling occurrence if appears before line 50
    first_50_lines = cleaned.splitlines()[:50]
    if any("Dribbling" in line for line in first_50_lines):
        cleaned_lines = cleaned.splitlines()
        for i in range(min(50, len(cleaned_lines))):
            if "Dribbling" in cleaned_lines[i]:
                cleaned_lines[i] = ""
                break
        cleaned = "\n".join(cleaned_lines)
    
    # Keep lines including empties to count positions properly
    lines = cleaned.splitlines()
    parsed = {}
    parsed['Name'] = get_line(lines, 1)
    parsed['Style'] = get_line(lines, 2)
    # Remove cm from height if present
    height = get_line(lines, 4)
    if height.endswith("cm"):
        height = height[:-2]
    parsed['Height'] = height
    parsed['Position'] = get_line(lines, 25)
    # Search for numeric attributes
    for label in STATS_LABELS:
        val = find_stat(cleaned, label)
        parsed[label] = val
    #print(parsed)  # Debugging print of all parsed data
    return parsed

def new_parse_file(file_path):
    # Ne parse: Take a txt, and make a dicctionary with the id:value that is in txt
    parsed_data = {}
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                key, value = line.split(":", 1)
                parsed_data[key.strip()] = value.strip()
    #print(parsed_data)  # Debugging print of the parsed data dictionary
    return parsed_data

# Compare Parsed data with a CSV file
# Only the attributes present in the CSV will be compared
# CSV Format attribute,min,ok,top,ponderation
# Make a ponderated score of the player based on the CSV thresholds
def compare_with_csv(parsed_data, csv_path):
    import csv
    csv_data = {}
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            attr = row['attribute']
            if int(row['ponderation']) != 0 and int(row['top']) != 0 and int(row['ok']) != 0 and int(row['min']) != 0:
                csv_data[attr] = {
                    'min': int(row['min']),
                    'ok': int(row['ok']),
                    'top': int(row['top']),
                    'ponderation': int(row['ponderation'])
                }
    score = 0
    total_ponderation = 0
    for attr, thresholds in csv_data.items():
        att_score = 0
        if attr in parsed_data and parsed_data[attr] is not None:
            val = parsed_data[attr]
            val = int(val)
            # If Attribute is Height Max_att_value is 210 else 110
            if attr == "Height":
                max_att_value = 210
            else:
                max_att_value = 110
            max_score_from_stats = 100
            ponderation = thresholds['ponderation']
            total_ponderation += ponderation
            if val >= thresholds['top']:
                att_score = ponderation * 1.0
                if max_att_value > thresholds['top']:
                    att_score += ponderation * 0.2 * (val - thresholds['top']) / (max_att_value - thresholds['top'])
                else:
                    print(f"\033[93mWarning: For attribute {attr}, top threshold {thresholds['top']} is greater or equal to max attribute value {max_att_value}\033[0m")
            elif val >= thresholds['ok']:
                att_score = ponderation * 0.7
                if thresholds['top'] > thresholds['ok']:
                    att_score += ponderation * 0.3 * (val - thresholds['ok']) / (thresholds['top'] - thresholds['ok'])
                else:
                    print(f"\033[93mWarning: For attribute {attr}, ok threshold {thresholds['ok']} is greater or equal to top threshold {thresholds['top']}\033[0m")
            elif val >= thresholds['min']:
                att_score = ponderation * 0.4
                if thresholds['ok'] > thresholds['min']:
                    att_score += ponderation * 0.3 * (val - thresholds['min']) / (thresholds['ok'] - thresholds['min'])
                else:
                    print(f"\033[93mWarning: For attribute {attr}, min threshold {thresholds['min']} is greater or equal to ok threshold {thresholds['ok']}\033[0m")
            else:
                if thresholds['min'] > 50:
                    att_score += ponderation * 0.4 * (val - 50) / (thresholds['min'] - 50)
                else:
                    print(f"\033[93mWarning: For attribute {attr}, min threshold {thresholds['min']} is less or equal to 50\033[0m")
            score += att_score
            #print(f"Attribute: {attr}, Value: {val}, Score: {att_score:.1f}")
            
    final_score = (score / total_ponderation) * max_score_from_stats if total_ponderation > 0 else 0
    
    return final_score

# Function that parse skills and premium skills from the cleaned text
def parse_skills(cleaned_text):
    # For cleaned_text left the words after a line how only has "Skills" on it
    # Remove everything before "\nSkills\n" included "Skills" line and empty lines before it
    skills_start = cleaned_text.find("\nSkills\n")
    skills_finish = cleaned_text.find("\n\n", skills_start + 1)
    if skills_start != -1:
        cleaned_text = cleaned_text[skills_start:]
        if skills_finish != -1:
            cleaned_text = cleaned_text[:skills_finish]
    #Remove the "Skills" word from the text
    cleaned_text = cleaned_text.replace("Skills", "")
    lines = cleaned_text.splitlines()
    # Separete Skills and Premium Skills sections
    skills_section = []
    premium_skills_section = []
    for line in lines:
        for premium_skill in PREMIUM_SKILL_LABELS:
            #print(f"Checking if '{premium_skill}' is in line: '{line}'")
            if premium_skill.lower() in line.lower():
                premium_skills_section.append(line)
        else:
            for skill in SKILL_LABELS:
                if skill.lower() in line.lower():
                    skills_section.append(line)
                    #print(f"Found skill '{skill}' in line: '{line}'")
            
    return skills_section, premium_skills_section

# Funcion that parse skills in new format
def parse_skills_new(cleaned):
    # Keep all the lines between "Skills" and "Biometrics"
    skills_section = []
    premium_skills_section = []
    skills_start = cleaned.find("Skills")
    bio_start = cleaned.find("Biometrics")
    #print(cleaned)
    #print(f"Skills start index: {skills_start}, Biometrics start index: {bio_start}")  # Debugging print
    if skills_start != -1 and bio_start != -1 and bio_start > skills_start:
        skills_text = cleaned[skills_start:bio_start]
        lines = skills_text.splitlines()
        # Remove first and last line from lines
        lines = lines[1:]
        #print(f"Extracted skills section lines: {lines}")  # Debugging print
        for line in lines:
            for premium_skill in PREMIUM_SKILL_LABELS:
                if premium_skill.lower() in line.lower():
                    premium_skills_section.append(line)
            else:
                for skill in SKILL_LABELS:
                    if skill.lower() in line.lower():
                        skills_section.append(line)
    
    return skills_section, premium_skills_section

def rate_skills_with_csv(skills, premium_skills, csv_path, pow=False):
    score = 0
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        skill_values = {}
        valid_skills = False
        for row in reader:
            # If row is "Skills" make valid the search for skills
            if valid_skills == False and row['attribute'] == "Skills":
                valid_skills = True
                continue
            elif valid_skills == True:
                attr = row['attribute']
                skill_values[attr] = {
                    'ponderation': int(row['ponderation'])
            }
        for skill in skills:
            if skill in skill_values:
                ponderation = skill_values[skill]['ponderation']
                score += ponderation / 1000.0
        for pskill in premium_skills:
            if pskill in skill_values:
                ponderation = skill_values[pskill]['ponderation']
                score += ponderation / 1000.0
        #print(f"Skills {skills}, Premium Skills {premium_skills} contributed to score: {score:.1f}")
        # Remove all PREMIUM_SKILLS from skill_values to avoid double counting
        for pskill in PREMIUM_SKILL_LABELS:
            if pskill in skill_values:
                del skill_values[pskill]
        #print(f"Remaining skills after removing premium skills: {skill_values.keys()}")
        # Remove all skill from skill_values to avoid double counting
        for skill in skills:
            if skill in skill_values:
                del skill_values[skill]
        #print(f"Remaining skills after removing normal skills: {skill_values.keys()}")
                
        # If POW is false sort the remaining skills by ponderation and take only top 5
        added = 0
        if not pow:
            remaining_skills = sorted(skill_values.items(), key=lambda x: x[1]['ponderation'], reverse=True)
            top_skills = remaining_skills[:5]
            #print(f"Top skills considered for score: {top_skills}")
            for skill, data in top_skills:
                ponderation = data['ponderation']
                added += ponderation / 1000.0
            score += added
                
    return score, added

# Function that parses biometrics from cleaned text
def parse_biometrics(cleaned_text):
    #print(cleaned_text)
    biometrics = {}
    # Take the fourth line of cleaned_text
    lines = cleaned_text.splitlines()
    if len(lines) >= 4:
        bio_line = lines[3]
    # Remove cm from bio line
    bio_line = bio_line.replace("cm", "")
    # Append bio_line to biometrics as atribute "Height"
    biometrics["Height"] = bio_line.strip()
    
    for label in BIOMETRICS_LABELS:
        pat = build_label_pattern(label)
        m = re.search(pat, cleaned_text, flags=re.IGNORECASE)
        if m:
            biometrics[label] = m.group(1)   
            
    #print(f"Biometrics parsed: {biometrics}")
    return biometrics

def parse_biometrics_new(cleaned):
    biometrics = {}
    # Fount Heigth and Weigth
    aux_labels = ["Height", "Weight"]
    for label in aux_labels:
        pat = build_label_pattern(label)
        m = re.search(pat, cleaned, flags=re.IGNORECASE)
        if m:
            biometrics[label] = m.group(1)
    
    for label in BIOMETRICS_LABELS:
        pat = build_label_pattern(label)
        m = re.search(pat, cleaned, flags=re.IGNORECASE)
        if m:
            biometrics[label] = m.group(1)   
            
    #print(f"Biometrics parsed: {biometrics}")
    return biometrics

# Function that rates biometrics with csv
def rate_biometrics_with_csv(biometrics, csv_path):
    quick_bio = 0
    strong_bio = 0
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        biometric_values = {}
        valid_biometrics = False
        for row in reader:
            # If row is "Bio" make valid the search for biometrics
            if valid_biometrics == False and row['attribute'] == "Bio":
                valid_biometrics = True
                continue
            elif valid_biometrics == True:
                attr = row['attribute']
                biometric_values[attr] = {
                    'ponderation': int(row['ponderation'])
            }
                
        # Store Bio Off and Bio Def ponderations and remove them from biometric_values to avoid double counting
        quick_bio_ponderation = 0
        strong_bio_ponderation = 0
        if "Quick Bio" in biometric_values:
            quick_bio_ponderation = biometric_values["Quick Bio"]['ponderation']
            del biometric_values["Quick Bio"]
        if "Strong Bio" in biometric_values:
            strong_bio_ponderation = biometric_values["Strong Bio"]['ponderation']
            del biometric_values["Strong Bio"]

        #print(biometric_values)
        # Height Effecy, daquire height from biometrics
        height = int(biometrics["Height"])
        #print(f"Player Height: {height} cm")
        
        # Rate Off and Strong Biometrics
        for label, value in biometrics.items():
            if label in biometric_values:
                if label != "Height":
                    ponderation = biometric_values[label]['ponderation']
                    try:
                        val = int(value)
                        strong_bio  += (ponderation / 1000.0) * (val - 7 + (height - 180)/4)
                        if label == "Leg Length":
                            quick_bio   += (ponderation / 1000.0) * (7 - val + (180 - height)/4)
                    except:
                        continue
                
        # Add Quick Bio and Strong Bio ponderations
        quick_score = quick_bio_ponderation * quick_bio
        strong_score = strong_bio_ponderation * strong_bio
        if quick_score < 0:
            quick_score = 0
        if strong_score < 0:
            strong_score = 0
            
        score = strong_score + quick_score
        
    return score

# Function that parse configuration from a config.ini file
def parse_config():
    import configparser
    config = configparser.ConfigParser()
    config_path = Path("config.ini")
    normalize_factor = 120.0
    if config_path.exists():
        config.read(config_path)
        try:
            normalize_factor = float(config.get('general', 'normalize_factor'))
            att_ponderation = float(config.get('general', 'att_ponderation'))
            card_ponderation = float(config.get('general', 'card_ponderation'))
            skills_ponderation = float(config.get('general', 'skills_ponderation'))
            biometrics_ponderation = float(config.get('general', 'biometrics_ponderation'))
        except:
            print("Error reading configuration from config.ini, using default values")
            normalize_factor = 120.0
            att_ponderation = 100.0
            card_ponderation = 100.0
            skills_ponderation = 100.0
            biometrics_ponderation = 100.0
            
        #print(f"Using configuration from config.ini: normalize_factor={normalize_factor}, attribute_ponderation={att_ponderation}, card_ponderation={card_ponderation}, skills_ponderation={skills_ponderation}, biometrics_ponderation={biometrics_ponderation}")
        
    return normalize_factor, att_ponderation, card_ponderation, skills_ponderation, biometrics_ponderation

def rate_player(file_path, csv_path=Path("player_profiles.csv")):
    normalize_factor, att_ponderation, card_ponderation, skills_ponderation, biometrics_ponderation = parse_config()
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {path}")
        return None, 0
    
    # If Txt filename has "—" use new_parse_file, else use parse_file
    if "—" in path.name:
        result = new_parse_file(path)
        #print(f"Parsed data for player using new_parse_file: {result}")
        # Remove from Dictionary all keey with values =''
        result = {k: v for k, v in result.items() if v != ''}
        # Change Weak Foot Accuracy key to Weak Foot Acc
        if "Weak Foot Accuracy" in result:
            result["Weak Foot Acc"] = result.pop("Weak Foot Accuracy")
        #print(f"Parsed data after removing empty values: {result}")
    else:
        result = parse_file(path)
    
    #print(f"Parsed data for player: {result}")
    # Perform comparison with every *.csv file 
    final_score = 0
    base_attr_score = 0
    skills_bonus = 0
    card_bonus = 0
    biometrics_bonus = 0
            
    csv_path = Path(csv_path)
    if csv_path.exists():
        #print(f"Comparing with profile: {csv_path}")
        # Round final score to 1 decimal place
        base_attr_score = compare_with_csv(result, csv_path)
        #print(f"Base Score from attributes: {base_attr_score:.1f}")
        
        # Get epic_dif and off_def_dif from csv comparation file
        epic_dif = 0
        off_def_dif = 0
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['attribute'] == 'epic_dif':
                    try:
                        epic_dif = int(row['ponderation'])/1000
                    except:
                        epic_dif = 1.025
                if row['attribute'] == 'off_def_dif':
                    try:
                        off_def_dif = int(row['ponderation'])/1000
                    except:
                        off_def_dif = 0.875
                if row['attribute'] == 'weak_foot_usage':
                    try:
                        weak_foot_usage_ponderation = int(row['ponderation'])/1000
                    except:
                        weak_foot_usage_ponderation = 0.3
                if row['attribute'] == 'weak_foot_acc':
                    try:
                        weak_foot_acc_ponderation = int(row['ponderation'])/1000
                    except:
                        weak_foot_acc_ponderation = 0.3
                if row['attribute'] == 'player_form':
                    try:
                        form_ponderation = int(row['ponderation'])/1000
                    except:
                        form_ponderation = 0.2
                if row['attribute'] == 'injury_resistance':
                    try:
                        injury_resistance_ponderation = int(row['ponderation'])/1000
                    except:
                        injury_resistance_ponderation = 0.1
        
        # To Final Score add "Weak Foot Usage, Weak Foot Acc, Form, Injury Resistance bonus:
        bonus_attrs = ["Weak Foot Usage", "Weak Foot Acc", "Form", "Injury Resistance"]
        bonus_poderations = [weak_foot_usage_ponderation, weak_foot_acc_ponderation, form_ponderation, injury_resistance_ponderation]
        bonus = 0
        for attr, ponderation in zip(bonus_attrs, bonus_poderations):
            val = int(result.get(attr, 0))
            #print(f"Original value for {attr}: {val}")
            if attr == "Form":
                if "Epic" in file_path or "BigTime" in file_path:
                    #print(f"Applying form bonus adjustment for Epic/BigTime card: original value {val}")
                    if val == 0:
                        val = 3.876
                    elif val == 1:
                        val = 3.002
                    else:
                        val = 2.865
                    #print(f"Adjusted Form value: {val:.2f}")
                else:
                    #print(f"Form value for non-Epic/BigTime card: {val}")
                    if val == 0:
                        val = 1.552
                    elif val == 1:
                        val = 1.0
                    else:
                        val = 1.456
                    #print(f"Adjusted Form value for non-Epic/BigTime card: {val:.2f}")
            if val is not None:
                bonus += ponderation * (val)
            #print(f"Attribute: {attr}, Value: {val}, Ponderation: {ponderation}, Contribution to bonus: {ponderation * val:.1f}")
        card_bonus = bonus
        #print(f"Added bonus from attributes {bonus_attrs}: {card_bonus:.1f}")
        # Add epic_dif point if file names contain "Epic" or "BigTime"
        if "Epic" in file_path or "BigTime" in file_path:
            #print(f"Added epic_dif: {epic_dif}")
            card_bonus += epic_dif
        # Add off_def_dif points if Style is "Defensive Goalkeeper"
        if result.get("Style", "") == "Defensive Goalkeeper":
            #print(f"Added off_def_dif: {off_def_dif}")
            card_bonus += off_def_dif       
        #print(f"Total Card Bonus: {card_bonus:.1f}")
        
        # Rate skills and premium skills
        cleaned = clean_text_keep_space_and_newline(path.read_text(encoding='utf-8', errors='ignore'))
        # If filename has "—" 
        if "—" in path.name:
            skills_found, premium_skills_found = parse_skills_new(cleaned)
        else:
            #print(cleaned)
            skills_found, premium_skills_found = parse_skills(cleaned)
        
        # POW Detection, if file name contains "POW" set pow to True
        if "POW" in file_path.upper():
            pow = True
        else:
            pow = False
        
        #print(f"Skills found: {skills_found}, Premium Skills found: {premium_skills_found}")
        
        skills_bonus, added_skills = rate_skills_with_csv(skills_found, premium_skills_found, csv_path, pow=pow)
        #print(f"Added skills bonus: {skills_bonus:.1f}")
        
        # Biometrics
        # If filename has "—" use new_parse_file to get biometrics, else use parse_biometrics
        if "—" in path.name:
            biometrics = parse_biometrics_new(cleaned)
        else:
            biometrics = parse_biometrics(cleaned)
        #print(f"Biometrics found for player {result.get('Name', 'Unknown')}: {biometrics}")
        biometrics_bonus = rate_biometrics_with_csv(biometrics, csv_path)
        #print(f"Added biometrics bonus: {biometrics_bonus:.1f}")
        
    # Normalize outputs
    base_attr_score = base_attr_score * att_ponderation / normalize_factor
    #print(f"Base Attribute Score after ponderation and normalization: {base_attr_score:.1f}")
    card_bonus = card_bonus * card_ponderation / normalize_factor
    #print(f"Card Bonus after ponderation and normalization: {card_bonus:.1f}")
    skills_bonus = skills_bonus * skills_ponderation / normalize_factor
    #print(f"Skills Bonus after ponderation and normalization: {skills_bonus:.1f}")
    added_skills = added_skills * skills_ponderation / normalize_factor
    #print(f"Added Skills Bonus after ponderation and normalization: {added_skills:.1f}")
    biometrics_bonus = biometrics_bonus * biometrics_ponderation / normalize_factor
    #print(f"Biometrics Bonus after ponderation and normalization: {biometrics_bonus:.1f}")
    final_score = base_attr_score + card_bonus + skills_bonus + biometrics_bonus
    #print(f"Final Score: {final_score:.1f}")
     
    # Return Name and Final Score       
    return result.get('Name', 'Unknown'), final_score, base_attr_score, card_bonus, skills_bonus, added_skills, biometrics_bonus

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 rate_player.py [-h|--help] <player_file> [csv_profile]")
        sys.exit(1)
    
    # Check for help flags
    if sys.argv[1] in ['-h', '--h', '-help', '--help']:
        print_help()
        sys.exit(0)
    
    file_path = sys.argv[1]
    csv_path = Path("player_profiles.csv")
    
    # Optional CSV profile argument
    if len(sys.argv) > 2:
        csv_path = Path(sys.argv[2])
    
    name, score, base_attr_score, card_bonus, skills_bonus, added_skills, biometrics_bonus = rate_player(file_path, csv_path=csv_path)
    if name:
        print(f"Player {name} rated with score: {score:.1f} (Base: {base_attr_score:.1f}, Card Bonus: {card_bonus:.1f}, Skills Bonus: {skills_bonus:.1f}, Added Skills Bonus: {added_skills:.1f}, Biometrics Bonus: {biometrics_bonus:.1f})")

def print_help():
    help_text = """
    Player Rating System
    
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
    """
    print(help_text)

if __name__ == "__main__":
    main()