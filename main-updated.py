def main():

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

    # split arrays into entries
    def convert_php_to_python(php):
        entries = re.split(r'Array\s*\(', php)
        parsed = []

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
    filename = current_type + ".csv"
    def write_csv(converted_data):
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for item in converted_data:
                row = {}
                stats = item.get('statsID', {})
                for k in fields:
                    row[k] = item.get(k, '')
                writer.writerow(row)

    def write_python_data(parsed_data, filename='raw_data.py'):
        with open(filename, 'w') as f:
            f.write("# Auto-generated parsed data\n")
            f.write("data = ")
            pprint.pprint(parsed_data, stream=f, width=120)


    ready_to_write_data = convert_php_to_python(raw_data)


    write_csv(ready_to_write_data)
    print(f"CSV file written as '(filename)")


    write_python_data(ready_to_write_data)
    print("raw data converted to python and written as 'raw_data.py'")

main()
