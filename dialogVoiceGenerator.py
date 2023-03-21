from __future__ import annotations

import math
import os.path
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Union

import keyring
import requests
from elevenlabslib import ElevenLabsUser, ElevenLabsVoice, helpers

backgroundColor = "#2b2b2b"
buttonBackground = "#424242"
foregroundColor = "white"

def main():
    pathValid, apiKeyValid, dirValid = False, False, False
    path, saveDir = "",""
    api_key = keyring.get_password("renpy_TTS_dialog_generator", "elevenlabs")
    if api_key is None:
        api_key = ""
    user = None
    voiceList:list[ElevenLabsVoice] = []
    while not pathValid or not apiKeyValid or not dirValid:

        path, api_key, saveDir = get_filepath(path, api_key, saveDir)
        pathValid = os.path.isfile(path)
        dirValid = os.path.isdir(saveDir)

        user = ElevenLabsUser(api_key)
        try:
            voiceList = user.get_available_voices()
            apiKeyValid = True
            keyring.set_password("renpy_TTS_dialog_generator", "elevenlabs", api_key)
        except requests.exceptions.HTTPError:
            apiKeyValid = False
        if not apiKeyValid:
            show_text("Error! API Key incorrect or expired.")
        if not pathValid:
            show_text("Error! Could not find a file at the specified location.")
        if not dirValid:
            show_text("Error! Could not find a directory at the specified location.")

    #We have the path to the script and the list of voices.
    print(path)
    voiceNames = list()
    for voice in voiceList:
        voiceNames.append(f"{voice.initialName} ({voice.voiceID})")


    scriptLines = open(path,"r").readlines()
    columnIndexes:dict[str,int] = {}
    for idx,column in enumerate(scriptLines[0].split("\t")):
        columnIndexes[column.lower().replace("\n","")] = idx
    print(columnIndexes)

    dialogData = list()
    characters = dict()
    for idx, line in enumerate(scriptLines):
        if idx == 0:
            continue
        parts = line.split("\t")
        lineObject = dict()
        lineObject["identifier"] = parts[columnIndexes["identifier"]].strip()

        characterName = parts[columnIndexes["character"]].strip()
        lineObject["character"] = characterName if characterName != "" else "no character"
        characters[lineObject["character"]] = ""
        lineObject["dialogue"] = parts[columnIndexes["dialogue"]].strip()
        lineObject["scriptfile"] = parts[columnIndexes["filename"]].strip()
        dialogData.append(lineObject)
        print("")

    voiceAssociations:dict[str, Union[str,ElevenLabsVoice]] = create_combobox_gui(list(characters.keys()),voiceNames)
    voicelessCharacters = [key for key in voiceAssociations if voiceAssociations[key] == ""]
    for key in voicelessCharacters:
        del voiceAssociations[key]
    for key, value in voiceAssociations.items():
        voiceID = value[value.find("(")+1:value.find(")")]
        voiceAssociations[key] = user.get_voice_by_ID(voiceID)

    #We have the character names associated with voiceIDs.
    #The ones missing from this dict will be silent.
    print(voiceAssociations)

    skipAlreadyExisting = None

    for dialog in dialogData:
        if dialog["character"] not in voiceAssociations:
            continue    #Skip characters that have no voice assigned
        print("Generating audio for:")
        print(f'{dialog["identifier"]}\t{dialog["character"]}: {dialog["dialogue"]}')
        associatedVoice = voiceAssociations[dialog["character"]]
        filePath = os.path.join(saveDir,dialog["identifier"]) + ".mp3"
        if os.path.isfile(filePath) and skipAlreadyExisting is None:
            skipAlreadyExisting = choose_yes_no(
                "Warning! Found that some voice files already exist. Would you like to SKIP voice files that have already been generated, or would you like to overwrite them (to change the voice, for example)?",
                trueOption="Skip", falseOption="Overwrite")

        if os.path.isfile(filePath) and skipAlreadyExisting:
            print("File already exists and you chose to skip...")
        else:
            audioData = associatedVoice.generate_audio_bytes(dialog["dialogue"])
            helpers.save_bytes_to_path(filePath, audioData)

        print("")
    print("Done!")

def browse_file(entry):
    filetypes = [("Tab-separated files", "*.tab"), ("All files", "*.*")]
    file_path = filedialog.askopenfilename(initialdir=".", title="Select a .tab file", filetypes=filetypes)
    entry.delete(0, tk.END)
    entry.insert(0, file_path)

def browse_directory(entry):
    directory = filedialog.askdirectory(initialdir=".", title="Select the voice file save directory")
    entry.delete(0, tk.END)
    entry.insert(0, directory)

def get_filepath(defaultFile="", defaultApiKey="", defaultDir="") -> (str, str, str):
    root = tk.Tk()
    root.title("Select a .tab file")
    setup_style(root, backgroundColor, buttonBackground, foregroundColor)

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    frame.highlightthickness = 0

    dialog_file_label = ttk.Label(frame, text="Exported dialog.tab (with text tags stripped) path:")
    dialog_file_label.grid(row=0, column=0, padx=(10, 0), pady=(10, 0), sticky="w")

    dialog_file_entry = ttk.Entry(frame, width=50)
    dialog_file_entry.insert(0, defaultFile)
    dialog_file_entry.grid(row=0, column=1, padx=(0, 10), pady=(10, 0))

    browse_button = ttk.Button(frame, text="Browse", command=lambda: browse_file(dialog_file_entry))
    browse_button.grid(row=0, column=2, padx=(10, 5), pady=(10, 10), sticky="w")

    dir_label = ttk.Label(frame, text="Voice file save directory:")
    dir_label.grid(row=1, column=0, padx=(10, 0), pady=(10, 0), sticky="w")

    dir_entry = ttk.Entry(frame, width=50)
    dir_entry.insert(0, defaultDir)
    dir_entry.grid(row=1, column=1, padx=(0, 10), pady=(10, 0))

    browse_dir_button = ttk.Button(frame, text="Browse", command=lambda: browse_directory(dir_entry))
    browse_dir_button.grid(row=1, column=2, padx=(10, 5), pady=(10, 10), sticky="w")

    api_key_label = ttk.Label(frame, text="11.ai API Key:")
    api_key_label.grid(row=2, column=0, padx=(10, 0), pady=(10, 0), sticky="w")

    api_key_entry = ttk.Entry(frame, width=50, show="*")
    api_key_entry.insert(0, defaultApiKey)
    api_key_entry.grid(row=2, column=1, padx=(0, 10), pady=(10, 0))

    confirm_button = ttk.Button(frame, text="Confirm", command=lambda: root.quit())
    confirm_button.grid(row=3, column=2, padx=(5, 10), pady=(10, 10), sticky="e")

    root.mainloop()
    filePath = dialog_file_entry.get()
    api_key = api_key_entry.get()
    voice_file_directory = dir_entry.get()
    root.destroy()
    return filePath, api_key, voice_file_directory


def create_combobox_gui(list1, list2) -> dict[str, str]:
    def create_combobox(parent, label_text, options):
        label = ttk.Label(parent, text=label_text)
        label.grid(column=0, row=0, pady=(10, 0))
        combobox = ttk.Combobox(parent, values=options, state="readonly")
        combobox.grid(column=0, row=1, pady=(0, 10))
        return label_text, combobox

    def on_confirm():
        selections = {}
        all_filled = True

        for label, combobox in comboboxes:
            selection = combobox.get()
            if not selection:
                all_filled = False
            selections[label] = selection

        if all_filled:
            root.selected_values = selections
            root.quit()
        else:
            if choose_yes_no("You haven't picked a voice for every character! Are you sure you'd like to continue? Characters without a voice won't have any voice data generated.", rootWindow=root):
                root.selected_values = selections
                root.quit()

    root = tk.Tk()
    root.title("Assign voices")
    setup_style(root, backgroundColor, buttonBackground, foregroundColor)

    n_elements = len(list1)
    grid_size = math.ceil(math.sqrt(n_elements))

    frames = [[ttk.Frame(root) for _ in range(grid_size)] for _ in range(grid_size)]

    for i, frame_row in enumerate(frames):
        for j, frame in enumerate(frame_row):
            frame.grid(row=i, column=j, padx=(10, 10), pady=(10, 10))

    comboboxes = []
    for i, item in enumerate(list1):
        row = i // grid_size
        col = i % grid_size
        frame = frames[row][col]
        label, combobox = create_combobox(frame, item, list2)
        comboboxes.append((label, combobox))

    confirm_button = ttk.Button(root, text="Confirm", command=on_confirm)
    confirm_button.grid(row=grid_size, column=0, columnspan=grid_size, pady=(10, 10))

    root.selected_values = None
    root.mainloop()

    selected_values = root.selected_values
    root.destroy()
    return selected_values


def setup_style(app, backgroundColor, buttonBackground, foregroundColor):
    app.configure(bg=backgroundColor)
    app.option_add('*TCombobox*Listbox.foreground', foregroundColor)
    app.option_add('*TCombobox*Listbox.background', buttonBackground)
    style = ttk.Style()
    style.theme_use('clam')

    style.configure('.', background=backgroundColor, foreground=foregroundColor)
    style.configure('TLabel', background=backgroundColor, foreground=foregroundColor)
    style.configure('TFrame', background=backgroundColor)
    style.configure('TCheckbutton', background=backgroundColor, foreground=foregroundColor, fieldbackground=backgroundColor)
    style.configure('TCombobox', selectbackground=backgroundColor, fieldbackground=backgroundColor, background=backgroundColor)
    style.configure('TButton', background=buttonBackground, foreground=foregroundColor, bordercolor=buttonBackground)
    style.configure('TEntry', fieldbackground=backgroundColor, foreground=foregroundColor, insertcolor=foregroundColor, insertwidth=2)
    style.map('TCombobox',
              fieldbackground=[('readonly', backgroundColor)],
              selectbackground=[('readonly', backgroundColor)],
              foreground=[('readonly', foregroundColor)])  # Set a lighter shade of gray for lines

    style.map('TCheckbutton',
              background=[('active', buttonBackground)],  # Custom background color on hover
              foreground=[('active', foregroundColor)])  # Custom foreground (text) color on hover

def show_text(message):
    app = tk.Tk()
    app.attributes('-alpha', 0)
    setup_style(app, backgroundColor, buttonBackground, foregroundColor)
    show_custom_messagebox(app, "Info", message)
    app.destroy()

def show_custom_messagebox(app, title, message):
    messagebox_window = tk.Toplevel(app)
    messagebox_window.title(title)
    messagebox_window.configure(bg='#2b2b2b')  # Set the background color to match the dark theme
    messagebox_window.highlightthickness = 0  # Remove the default padding

    message_label = ttk.Label(messagebox_window, text=message, padding=(20, 20))
    message_label.grid(row=0, column=0, columnspan=2)

    ok_button = ttk.Button(messagebox_window, text="OK", width=10, command=messagebox_window.destroy)
    ok_button.grid(row=1, column=0, columnspan=2, pady=(0, 20))

    messagebox_window.transient(app)
    messagebox_window.grab_set()
    app.wait_window(messagebox_window)

def choose_yes_no(prompt: str, trueOption: str = "Yes", falseOption: str = "No", rootWindow:tk.Tk=None) -> bool:
    result = list()
    def on_yes_click():
        result.append(True)
        yesno_window.destroy()

    def on_no_click():
        result.append(False)
        yesno_window.destroy()

    # Initialize window
    if rootWindow is None:
        window = tk.Tk()
        window.title("Question")
        window.attributes('-alpha', 0)
        setup_style(window, backgroundColor, buttonBackground, foregroundColor)
    else:
        window = rootWindow

    yesno_window = tk.Toplevel(window)
    yesno_window.title("")
    setup_style(yesno_window, backgroundColor, buttonBackground, foregroundColor)
    # Create and place the prompt label
    prompt_label = ttk.Label(yesno_window, text=prompt, wraplength=300)
    prompt_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    # Create and place the yes button
    yes_button = ttk.Button(yesno_window, text=trueOption, command=on_yes_click)
    yes_button.grid(row=1, column=0, padx=10, pady=10)

    # Create and place the no button
    no_button = ttk.Button(yesno_window, text=falseOption, command=on_no_click)
    no_button.grid(row=1, column=1, padx=10, pady=10)

    # Center the window
    yesno_window.transient(window)
    yesno_window.grab_set()
    window.wait_window(yesno_window)
    return result[0]

if __name__ == "__main__":
    main()


