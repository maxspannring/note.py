#!/usr/bin/python3
# Simple Note taking application,
# Max Spannring, Nov 2020


# imports
import argparse
import base64
import csv
import os
import sys
import time


# Global Variables
NOTEFILE_NAME = "notes.csv"                 # filename
NOTEFILE_DIR = f"{os.path.expanduser('~')}/.notescript"       # path to dir
NOTEPATH = NOTEFILE_DIR + "/" +  NOTEFILE_NAME


# handles command line arguments given to the script
parser = argparse.ArgumentParser(description = "A simple note taking application, useful for storing UNIX commands.",
                                epilog = ("\033[1m~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
                                    "written by Max Spannring, Nov 2020\n"
                                    "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\033[0m"),
                                formatter_class=argparse.RawDescriptionHelpFormatter)                  
parser.add_argument("inputText",
                    help="the text that you want to store",
                    metavar="notetext",
                    default="",
                    nargs="*")         
parser.add_argument("-l", "--list",
                    help="list all notes",
                    action="store_true")                   
parser.add_argument("-s", "--search",
                    help="search your notes",
                    metavar="SEARCHSTRING")
parser.add_argument("-r", "--remove",
                    help="removes the note with the id provided",
                    metavar="ID")


# checks if Notefile exist, creates it if it doesn't
if os.path.isfile(NOTEPATH):
    #loads noteset-database from csv file
    noteset = []
    comments = []   # seperate array for everthing besides notes
    with open(NOTEPATH, "r") as notefile:
        reader = csv.reader(notefile)
        for line in reader:
            if line[0].isnumeric(): # only appends valid entries
                decodedNote = base64.b64decode(line[2].encode("utf-8"))
                decodedNote = decodedNote.decode("utf-8")
                noteset.append([line[0], line[1], decodedNote])
            else:
                comments.append(line)
            
    notefile.close()
else:
    print("ERROR: the note file could not be found.")
    dir_created, file_created = False, False
    try:
        print(f"trying to create folder under {NOTEFILE_DIR}...")
        os.makedirs(NOTEFILE_DIR)
        dir_created = True
    except FileExistsError:
        print("looks like this folder already exists...")
        dir_created = True
    except PermissionError:
            print("ERROR: Directory could not be created(PermissionError).*Are you Root?*")
    try:
        print(f"trying to create file under {NOTEPATH}...")
        new_notefile = open(NOTEPATH, "w+")
        new_notefile.write("This is the data file for note.py, a simple note taking application.\n")
        new_notefile.write("Only lines that start with valid Id's are considered, the rest is ignored.\n")
        new_notefile.write("id,date,content\n")
        new_notefile.close()
        file_created = True
    except FileNotFoundError:
        print("ERROR: File could not be created.")
    if file_created and dir_created:
        print("\033[96mNotefile successfully created.\033[0m")
        noteset = []


# definitions of all 4 main functions (add,list,search,remove)
def addNote(inputText):
    id = 0
    try: id = int(noteset[-1][0]) + 1
    except: pass
    timestamp = time.strftime("%H:%M %d.%b %Y", time.localtime())
    encodedInputText = inputText.encode("utf-8")
    encodedInputText = base64.b64encode(encodedInputText)
    encodedInputText = encodedInputText.decode("utf-8")
    with open(NOTEPATH, "a") as notefile:
        notefile.write(f"{id}, {timestamp}, {encodedInputText}\n")
        notefile.close()

#gets kinda complicated with the highlight feature, but whatever
def listNotes(notesetArray, highlight = None):
    id_width, content_width = 0,0
    max_content_width = int(os.get_terminal_size()[0] // 1.9)    # dynamic table size
    datestamp_width = 19    # stays fixed
    # find out how wide the entries are
    for row in notesetArray:
        id_width = len(row[0]) if len(row[0]) > id_width else id_width
        content_width = len(row[2]) if len(row[2]) > content_width else content_width
    # sets upper boundary for width
    if content_width >= max_content_width: content_width = max_content_width
    # begin printing table
    print("┌─" + "─"*(id_width - 1) + "\033[33mNOTES\033[0m" + "─"*(datestamp_width - 2) + "┬─" + "─"*content_width + "─┐")
    for row in notesetArray:
        note_id = row[0]
        timestamp = row[1]
        ncontent, content = row[2], row[2]
        # split lines if too large
        if len(content) >= max_content_width:
            number_of_linebreaks = len(content)//(max_content_width + 1)
            line_content = content[:max_content_width]
            if highlight:
                line_content = line_content.replace(highlight, "\033[35m" + highlight + "\033[0m")
            print(("│" + " " + note_id + " "*(id_width - len(note_id)) + " │"
                            + timestamp + " │ "
                            + line_content + " │"))
            for i in range(number_of_linebreaks):
                i += 1
                line_content = content[max_content_width*i:max_content_width*(i+1)]
                if highlight:
                                content[max_content_width*i:max_content_width*(i+1)].replace(highlight, "\033[35m" + highlight + "\033[0m")
                print("│ " +" "*id_width + " │" + " "*datestamp_width + "│ " + 
                        line_content + 
                        " "*(content_width - len(content[max_content_width*i:max_content_width*(i+1)])) + " │")
        else:
            if highlight:
                ncontent = content.replace(highlight, "\033[35m" + highlight + "\033[0m")
            print(("│" + " " + note_id + " "*(id_width - len(note_id)) + " │"
                + timestamp + " │ "
                + ncontent + " "*(content_width - len(content)) + " │"))
    print("└─" + "─"*id_width + "─┴" + "─"*datestamp_width + "┴─" + "─"*content_width + "─┘")    


def searchNotes(searchTerm):
    searchedNoteset = []
    for note in noteset:
        if searchTerm in note[2]:
            searchedNoteset.append(note)
    if len(searchedNoteset) == 0:
        print("\033[91mNo results ):\033[0m")
        return
    listNotes(searchedNoteset, highlight=searchTerm)

def removeNote(note_id):
    newNoteset = []
    if not note_id.isnumeric():
        print("\033[91mArgument has to be numeric\033[0m")
        return
    for note in noteset:
        if note[0] == note_id:
            consent = input(f"Do you really want to delete the following note? y/N\n\033[3m{note[2]}\033[0m\n")
            if consent != "y":
                newNoteset.append(note)
            else:
                print("\033[96mnote deleted\033[0m")
        else:
            newNoteset.append(note)
    with open(NOTEPATH, "w") as notefile:
            new_note_id = 0
            for comment in comments:
                notefile.write(",".join(comment) + "\n")
            for note in newNoteset:
                timestamp = note[1]
                noteText = note[2]
                encodedNoteText = noteText.encode("utf-8")
                encodedNoteText = base64.b64encode(encodedNoteText)
                encodedNoteText = encodedNoteText.decode("utf-8")
                notefile.write(f"{new_note_id},{timestamp},{encodedNoteText}\n")
                new_note_id  += 1
            notefile.close()
    
    
    

# parses Arguments and then decides what to do
arguments = parser.parse_args()
if arguments.list:
    listNotes(noteset)
    sys.exit(0)
elif arguments.search != None:
    searchNotes(arguments.search)
    sys.exit(0)
elif arguments.remove:
    removeNote(arguments.remove)
    sys.exit(0)
elif arguments.inputText != "":
    inputText = " ".join(arguments.inputText)
    addNote(inputText)

    

# finished
