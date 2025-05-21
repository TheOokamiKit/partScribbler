def partScribbler():

    # imports sys to allow for interaction with files and arguments from the command line
    import sys

    # imports csv function to allow writing to csv format
    import csv

    # imports regular expression to assist in formatting prep
    import re

    # imorts python print to export files to assit in debugging
    import pprint

    # check to make sure program is passed a target file
    if len(sys.argv) != 2:
        raise Exception("Usage: python3 main.py <path_to_file>")
        sys.exit(1)

    #uses the provided file path to open the file and outputs it's contents into a string
    def file_to_string(filepath):
        with open(filepath) as f:
            file_contents = f.read()
            return str(file_contents)

    # takes file and converts to string using provided file path when running program
    file_as_string = file_to_string(sys.argv[1])

    # takes previously imported string and replaces the [ID] tag in the sub array with a new non duplicated name to prevent issues in output when filtering to only desired fields. Also removes the leading "(" of the sub array
    raw_data = file_as_string.replace("""[statsID] => Array
        (
            [ID]""","""[statsID] => Array
            [subID]""")

    # removes the ")" leftover from the sub array as well as the blank line below
    raw_data = raw_data.replace("""        )

    [""","""    [""")

    # un-indents the [subID] arrays
    raw_data = raw_data.replace("            ","    ")

    # holding variable for data once converted. Seperated to prevent reconverting data each time
    ready_to_write_data = []

    # sorted lists by part type
    Cockpit = []
    Mobility = []
    Weapon = []
    Armor = []
    Generator = []
    Aux = []
    Spacer = []
    Other = []


    # split arrays into entries
    def convert_php_to_python(php):
        entries = re.split(r'Array\s*\(', php)

        #skipping first entery since it will be blank due to the first found split instance being at the begining
        for entry in entries[1:]:
            obj = {}
            lines = entry.strip().splitlines()
            for line in lines:
                line = line.strip()
                match = re.match(r'\[([^\]]+)\] => (.+)', line)
                if match:
                    key, value = match.groups()
                    if value.isdigit():
                        value = int(value)
                    else:
                        try:
                            value = float(value)
                        except ValueError:
                            value = value.strip()
                    obj[key] = value
            ready_to_write_data.append(obj)
        return

    # sort directory of parts into catigories and calculate additional stats evaluations that are commonly used in the spreadsheet
    def sort_parts(list_of_parts):
        for part in list_of_parts:

            # Cockpit part calculations commonly used in the spreadsheet
            if part["parttype"] == 'Cockpit':
                part["HP_Weight"] = part["hitpoints"] / part["weight"]
                part["NetEnergy"] = part["energygen"] - part["energyuse"]
                part["Cooling_Weight"] = part["cooling"] / part["weight"]
                part["HeatCapacity"] = part["heatThreshold"] - part["heatgen"] + part["cooling"]
                part["TotalWeapons"] = part["weapongroups"] * part["weaponspergroup"]
                Cockpit.append(part)

            # Mobility part calculate commonly used in the spreadsheet
            elif part["parttype"] == 'Mobility':
                part["HeatCapacity"] = part["heatThreshold"] - part["heatgen"] + part["cooling"]
                part["MaxSpeed"] = part["forwardspeed"] * 4.1738
                part["NetEnergy"] = part["energygen"] - part["energyuse"]
                Mobility.append(part)

            # Weapon part calculations for custom stats and renaming stats for ease of readablity.
            elif part["parttype"] == 'Weapon':
                # current workaround for weapon damage not being reported by type in input data. Handles known exceptions that do both types first.
                if part["partname"] == "Screamer Rocket" or part["partname"] == "Gustaf - X2":
                    part["BlastDamage"] = part["damage"]
                    part["KineticDamage"] = part["damage"]
                elif part.setdefault("blastArea",0) > 0:
                    part["BlastDamage"] = part["damage"]
                    part["KineticDamage"] = 0
                else:
                    part["BlastDamage"] = 0
                    part["KineticDamage"] = part["damage"]

                part["NetEnergy"] = part["energygen"] - part["energyuse"]
                part["Cooling_Weight"] = part["cooling"] / part["weight"]
                part["HP_Weight"] = part["hitpoints"] / part["weight"]
                part["DamageCapacity"] = (part["BlastDamage"] + part["KineticDamage"]) * part["shotsperfire"] * part["bulletsperclip"]
                part["DC_Weight"] = part["DamageCapacity"] / part["weight"]
                part["RateOfFire_BPM"] = 60 / (part["firerate"] + (part.setdefault("firedelay",0.1) * (part["burstfire"] - 1) ) )
                part["ammo"] = part["bulletsperclip"]
                part["TimeTilEmptyM"] = part["ammo"]  / part["burstfire"] / part["RateOfFire_BPM"]
                if part["spreadX"] > part["spreadY"]:
                    part["MaxSpread"] = part["spreadX"]
                else:
                    part["MaxSpread"] = part["spreadY"]

                #todo change initialspeed to MaximumSpeed once serge is able to pull stat from game files. Currently rockets look bad as they accelerate mid flight. Working with what is available currently
                if part["initialspeed"] > 1:
                    part["TimeToMaxRange"] = part["range"] / part["initialspeed"]
                else:
                    part["TimeToMaxRange"] = 0

                part["DP_S"] = ( (part["BlastDamage"] + part["KineticDamage"]) * part["RateOfFire_BPM"] * part["burstfire"] * part["shotsperfire"]) / 60
                part["DP_S_Weight"] = part["DP_S"] / part["weight"]
                part["%_base_HP_M"] = ( ( (part["BlastDamage"] * 2) + part["KineticDamage"]) * part["RateOfFire_BPM"] * part["burstfire"] * part["shotsperfire"]) / 21000
                part["%_base_HP_M_W"] = part["%_base_HP_M"] / part["weight"]
                part["HeatP_S"] = part["impactHeat"] * part["RateOfFire_BPM"] * part["burstfire"] * part["shotsperfire"] / 60
                part["BurstDamage"] = (part["BlastDamage"] + part["KineticDamage"]) * part["burstfire"] * part["shotsperfire"]
                part["BurstDamage_W"] = part["BurstDamage"] / part["weight"]
                part["BurstHeat"] = part["impactHeat"] * part["burstfire"] * part["shotsperfire"]
                part["BurstHeat_W"] = part["BurstHeat"] / part["weight"]
                #todo 200m accuracy math
                #todo 500m accuracy math
                #todo max range accuracy math


                Weapon.append(part)

            elif part["parttype"] == 'Armor':
                Armor.append(part)

            elif part["parttype"] == 'Generator':
                Generator.append(part)

            elif part["parttype"] == 'Aux':
                Aux.append(part)

            elif part["parttype"] == 'Spacer':
                Spacer.append(part)

            else:
                Other.append(part)

    # list of stats to include in csv file. all others will be ignored

    fields_Cockpit = [
        "partname","subType","weight","HP_Weight","hitpoints","armor","energygen","energyuse","NetEnergy","heatgen","cooling","Cooling_Weight","heatThreshold","HeatCapacity",
        "weapongroups","weaponspergroup","TotalWeapons","aimstability","firedelay","cost","manufacturer","description","unlock","ID"
        ]

    fields_Mobility = [
        "partname","subType","load","hitpoints","armor","NetEnergy","energygen","energyuse","heatgen","HeatCapacity","cooling","heatThreshold","MaxSpeed",
        "forwardspeed","reversespeed","stability","shockabsorb","acceleraction","deacceleration","braking","turning","rotationspeed",
        "cost","manufacturer","description","unlock","ID"
        ]

    fields_Weapon = [
        "partname","subType","DP_S","DP_S_Weight","%_base_HP_M","%_base_HP_M_W","KineticDamage","BlastDamage","BurstDamage","BurstDamage_W","BurstHeat","BurstHeat_W","force",
        "initialspeed","TimeToMaxRange","spreadX","spreadY","MaxSpread","kickforce","range","ammo","RateOfFire_BPM","firerate","TimeTilEmptyM","DamageCapacity","DC_Weight",
        "hitpoints","HP_Weight","armor","weight","NetEnergy","heatgen","cooling","Cooling_Weight","heatThreshold","burstfirerate","shotsperfire","burstfire","reloadtime",
        "impactHeat","blastArea","lifetime","cost","manufacturer","description","unlock","ID"
        ]

    fields_Armor = [
        "partname","subType","ID","weight","hitpoints","armor","heatThreshold","cooling","heatgen","energygen","energyuse",
        "cost","manufacturer","description","unlock"
        ]

    fields_Generator = [
        "partname","subType","ID","weight","hitpoints","armor","energygen","energyuse","heatgen","cooling","heatThreshold",
        "cost","manufacturer","description","unlock"
        ]

    fields_Aux = [
        "partname","subType","ID","weight","hitpoints","armor","energygen","energyuse","heatgen","cooling","heatThreshold",
        "cost","manufacturer","description","unlock"
        ]

    fields_Spacer = [
        "partname","subType","ID","weight","hitpoints","armor","energygen","energyuse","heatgen","cooling","heatThreshold",
        "cost","manufacturer","description","unlock"
        ]

    # function to write to file

    def write_csv(sorted_data,part_type,fields_to_write):
        filename = part_type + ".csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields_to_write)
            writer.writeheader()
            for item in sorted_data:
                row = {}
                stats = item.get('statsID', {})
                for k in fields_to_write:
                    row[k] = item.get(k, '')
                writer.writerow(row)

    def write_python_data(sorted_data,part_type):
        filename = part_type + '.py'
        with open(filename, 'w') as f:
            f.write("# Auto-generated parsed data\n")
            f.write("data = ")
            pprint.pprint(sorted_data, stream=f, width=120)


    # call to convert data and store it in ready_to_write_data directory
    convert_php_to_python(raw_data)

    # call to sort ready_to_write_data and store sorted data in directories by part type
    sort_parts(ready_to_write_data)

    # call to write to csv file for each part type
    write_csv(Cockpit,"Cockpit",fields_Cockpit)
    write_csv(Mobility,"Mobility",fields_Mobility)
    write_csv(Weapon,"Weapon",fields_Weapon)
    write_csv(Armor,"Armor",fields_Armor)
    write_csv(Generator,"Generator",fields_Generator)
    write_csv(Aux,"Aux",fields_Aux)
    write_csv(Spacer,"Spacer",fields_Spacer)

    # call to write any new/uncaught part types to a python file for inspection
    write_python_data(Other,"Other")

partScribbler()
