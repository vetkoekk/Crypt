# Crypt
This is a basic encryption software I made in python using tkinter and sqlite3 for a school project.  

The program automatically encrypts all files in a specified folder on startup using a custom encryption method in which the text in a file is converted to Unicode before being multiplied by a randomly selected multiplier, with said multiplier being increased by a randomly selected step value after each character. The line number, multiplier and step are then stored to a database so that the program will be able to decrypt the file and a specific sting of characters is inserted into to the beginning of the file in order to identify any encrypted files and not encrypt them again on subsequent runnings of the program.
