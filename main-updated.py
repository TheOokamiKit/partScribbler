def main():

    # imports sys to allow for interaction with files and arguments from the command line
    import sys

    # imports csv function to allow writing to csv format
    import csv

    # imports regular expression to assist in formatting prep
    import re

    # check to make sure program is passed a target file
    if len(sys.argv) != 2:
        raise Exception("Usage: python3 main.py <path_to_file>")
        sys.exit(1)

    #uses the provided file path to open the file and outputs it's contents into a string
    def file_to_string(filepath):
        with open(filepath) as f:
            file_contents = f.read()
            return str(file_contents)

    raw_data = file_to_string(sys.argv[1])

    # split arrays into entries
    def convert_php_to_python(php):
        entries = re.split(r'Array\s*\(', php)
        parsed = []

        for entry in entries[1:]:
            obj = {}
            stats = {}
            current = obj
            lines = entry.strip().splitlines()
            for line in lines:
                line = line.strip()
                if 'statsID' in line and 'Array' in line:
                    current = stats
                    continue
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
                    current[key] = value
            obj['statsID'] = stats
            parsed.append(obj)

        return parsed

    # list of stats to include in csv file. all others will be ignored
    fields = [
        "partname","subType","ID", "hitpoints", "armor", "energyuse", "heatgen", "cooling", "weight",
        "range", "lifetime", "firerate", "burstfirerate", "force", "damage",
        "bulletsperclip", "shotsperfire", "burstfire", "reloadtime",
        "initialspeed", "spreadX", "spreadY", "kickforce"
    ]

    # write to file
    current_type = "weapon"
    filename = f"(current_type).csv"
    def write_csv(converted_data):
        top_level_fields = {"partname","subType","ID", "hitpoints", "armor", "energyuse", "heatgen", "cooling", "weight"}
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for item in converted_data:
                row = {}
                stats = item.get('statsID', {})
                for k in fields:
                    if k in top_level_fields:
                        row[k] = item.get(k, '')
                    else:
                        row[k] = stats.get(k, '')
                writer.writerow(row)

    ready_to_write_data = convert_php_to_python(raw_data)
    write_csv(ready_to_write_data)
    print(f"CSV file written as '(filename)")

main()
