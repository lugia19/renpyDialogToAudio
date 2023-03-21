# Renpy dialog voice generator

Generates voice files based on a dialog.tab file (with text tags stripped).


The TTS is generated using [elevenlabs](https://elevenlabs.io), with my `elevenlabslib` library.

When you run the program, it will show a GUI that will prompt you to specify:
- The dialog file
- The directory in which to save the audio files
- Your API key (will be stored in the system keyring for later runs)

After this it will pull a list of all voices available to your elevenlabs account, and will ask you to assign a voice to each character found in the dialog export.

It will then generate the audio files and save them as `{identifier}.mp3`, ready to be used with the auto voice option.

See here [LINK TBA]() for a usage example.

## Installation

1) Download this repo `git clone TBA`
2) Open `run.bat`

In case you're not on windows, run.bat just creates a venv and install the requirements from requirements.txt, then runs the script, so you can just do that manually.

In addition, it will also perform a git pull whenever it's run.