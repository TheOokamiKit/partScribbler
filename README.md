# partScribbler
A script to process MAV part data to a usable spreadsheet format

To use:
Run the python script in terminal/command line with the local path to the part data in php format as the second argument.

IE: python3 partScribbler.py parts_0_8_4_7.txt

Upon running the command it will output seven .csv files, one for each part type, as well as a Other.py that will contain the raw data of any part that was not included in the other lists (just to have a quick way to check if a new part type gets added).


The part data can be found from Rak Sal Ind. website here: https://www.raksal.com/stats/allstats.php (Note: you will need to save the data to a local file for processing as the script does not support a web address currently)

Credit and Thanks to:

cyberdogs7 over at Bombdog Studios for his dedication to making M.A.V. - https://bombdogstudios.com/

sergedavid over at Rak Sal Industries for pulling the data from the game files and creation of the server mod that makes it possible - https://www.raksal.com/
