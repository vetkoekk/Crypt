import os
import random
import sqlite3
import tkinter as tk
from tkinter import messagebox


class App:
    def __init__(self):
        self.data = sqlite3.Connection("encryptionData.db")
        self.cursor = self.data.cursor()

        self.root = tk.Tk()
        self.root.withdraw()

        self.makeDatabase()
        self.checkFirstRun()

    def makeDatabase(self):
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Data (
                    path VARCHAR,
                    line INT,
                    mult INT,
                    step INT
                );
            """)
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Code (
                    "exists" INT,
                    code VARCHAR
                );
            """)
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Directory (
                    dir_path VARCHAR
                );
            """)
        self.data.commit

    def checkFirstRun(self):
        self.cursor.execute("SELECT 'exists' FROM Code;")
        exists = self.cursor.fetchone()

        if exists:
            self.loadDirectory()
            self.mainPage()
        else:
            self.firstOpen()

    def saveCode(self):
        code = self.codeEntry.get()
        if not code:
            messagebox.showerror("Error", "Please enter a code")
            return

        self.cursor.execute(
            """
            INSERT INTO Code ("exists", code)
            VALUES (?, ?);
            """,
            (1, code),
        )
        self.data.commit()
        self.window.destroy()
        self.directorySetup()

    def saveDirectory(self):
        directory = self.directoryEntry.get()
        if not directory:
            messagebox.showerror("Error", "Please enter a directory path")
            return

        if not os.path.isdir(directory):
            messagebox.showerror("Error", "Invalid directory path")
            return

        self.cursor.execute(
            """
            INSERT INTO Directory (dir_path)
            VALUES (?);
            """,
            (directory,),
        )
        self.data.commit()
        self.target_directory = directory
        self.window.destroy()
        self.mainPage()

    def verifyCode(self):
        enteredCode = self.codeEntry.get()

        self.cursor.execute("SELECT code FROM Code;")
        savedCode = self.cursor.fetchone()

        if not savedCode or enteredCode != savedCode[0]:
            messagebox.showerror("Error", "Incorrect code")
            return

        self.window.destroy()
        self.decrypt()
        self.decrypted()

    def loadDirectory(self):
        self.cursor.execute("SELECT dir_path FROM Directory LIMIT 1;")
        result = self.cursor.fetchone()
        if result:
            self.target_directory = result[0]
        else:
            self.target_directory = "/Users/tainebudd/Desktop/Files"  # fallback default

    def getDirs(self):
        self.paths = []
        for root, _, files in os.walk(self.target_directory):
            for filename in files:
                if filename.endswith(".txt"):
                    filePath = os.path.join(root, filename)
                    self.paths.append(filePath)

    def encrypt(self):
        self.getDirs()

        for i in range(len(self.paths)):
            with open(self.paths[i], "r+") as file:
                first = file.readline()
                file.seek(0)

                if first == "üalieuhǔaw4těwthrħarsgņ\n":
                    continue

                content = file.read().splitlines()

                file.seek(0)
                file.truncate()

                file.write("üalieuhǔaw4těwthrħarsgņ\n")

                for o in range(len(content)):
                    chars = list(str(content[o]))
                    mult = random.randint(1, 10)
                    step = random.randint(1, 5)

                    self.cursor.execute(
                        """
                        INSERT INTO Data (path, line, mult, step)
                        VALUES (?, ?, ?, ?)
                    """,
                        (str(self.paths[i]), str(o), str(mult), str(step)),
                    )
                    self.data.commit()

                    encrypted = []

                    for char in chars:
                        encrypted.append(str(ord(char) * mult))
                        mult += step
                    file.write(",".join(encrypted) + "|")

    def decrypt(self):
        self.getDirs()

        for i in range(len(self.paths)):
            lines = []

            with open(self.paths[i], "r+") as file:
                lines = file.readlines()
                lines = lines[1:]
                file.seek(0)
                file.truncate()
                file.writelines(lines)

            with open(self.paths[i], "r+") as file:
                content = file.read().strip()
                if not content:
                    continue

                lines = content.split("|")
                decrypted = []
                lines = [line for line in lines if line]

                for o in range(len(lines)):
                    split = lines[o].split(",")
                    split = [item for item in split if item]
                    if not split:
                        continue

                    self.cursor.execute(
                        """
                        SELECT mult, step FROM Data
                        WHERE path=? AND line=?;
                    """,
                        (self.paths[i], o),
                    )
                    fetch = self.cursor.fetchone()

                    if not fetch:
                        continue

                    mult, step = fetch
                    decryptedLine = []

                    for p in range(len(split)):
                        try:
                            decryptedChar = chr(int(int(split[p]) / mult))
                            decryptedLine.append(decryptedChar)
                            mult += step
                        except (ValueError, ZeroDivisionError):
                            continue
                    decrypted.append("".join(decryptedLine))
                file.seek(0)
                file.truncate()
                file.write("\n".join(decrypted))

        os.remove("encryptionData.db")

    def mainPage(self):
        self.encrypt()
        self.window = tk.Toplevel(self.root)
        self.window.title("Crypt")
        self.window.geometry("250x130")
        self.window.configure(bg="gainsboro")
        self.window.resizable(width=False, height=False)

        tk.Label(
            self.window,
            text="Your data has been encrypted\nEnter the decryption key",
            bg="gainsboro",
            fg="gray24",
        ).pack(fill="both", pady=5)

        self.codeEntry = tk.Entry(
            self.window, bg="alice blue", fg="dim gray", justify="center"
        )
        self.codeEntry.pack(pady=5)

        tk.Button(
            self.window,
            text="Enter",
            command=self.verifyCode,
            borderwidth=2,
            relief="flat",
        ).pack(pady=5)

        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def directorySetup(self):
        self.window = tk.Toplevel(self.root)
        self.window.title("Crypt")
        self.window.geometry("350x150")
        self.window.configure(bg="gainsboro")
        self.window.resizable(width=False, height=False)

        tk.Label(
            self.window,
            text="Enter the directory path to encrypt\n(e.g., /Users/yourname/Documents)",
            bg="gainsboro",
            fg="gray24",
        ).pack(fill="both", pady=5)

        self.directoryEntry = tk.Entry(
            self.window, bg="alice blue", fg="dim gray", justify="center"
        )
        self.directoryEntry.pack(pady=5, padx=10, fill="x")

        tk.Button(
            self.window,
            text="Enter",
            command=self.saveDirectory,
            borderwidth=2,
            relief="flat",
        ).pack(pady=5)

        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def firstOpen(self):
        self.window = tk.Toplevel(self.root)
        self.window.title("Crypt")
        self.window.geometry("250x130")
        self.window.configure(bg="gainsboro")
        self.window.resizable(width=False, height=False)

        tk.Label(
            self.window,
            text="Enter a decryption key\nIt will be used to decrypt your data",
            bg="gainsboro",
            fg="gray24",
        ).pack(fill="both", pady=5)

        self.codeEntry = tk.Entry(
            self.window, bg="alice blue", fg="dim gray", justify="center"
        )
        self.codeEntry.pack(pady=5)

        tk.Button(
            self.window,
            text="Enter",
            command=self.saveCode,
            borderwidth=2,
            relief="flat",
        ).pack(pady=5)

        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def decrypted(self):
        self.window = tk.Toplevel(self.root)
        self.window.title("Crypt")
        self.window.geometry("250x130")
        self.window.configure(bg="gainsboro")
        self.window.resizable(width=False, height=False)

        tk.Label(
            self.window,
            text="Your data has been decrypted\nRun the program again to encrypt",
            bg="gainsboro",
            fg="gray24",
        ).place(x=10, y=60)

        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def close(self):
        self.data.close()
        self.root.destroy()


app = App()
app.root.mainloop()
