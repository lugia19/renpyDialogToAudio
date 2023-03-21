# Renpy dialog voice generator

Generates voice files based on a dialog.tab file (with text tags stripped).


The TTS is generated using [elevenlabs](https://elevenlabs.io), with my `elevenlabslib` library.

When you run the program, it will show a GUI that will prompt you to specify:
- The dialog file
- The directory in which to save the audio files
- Your API key (will be stored in the system keyring for later runs)

After this it will pull a list of all voices available to your elevenlabs account, and will ask you to assign a voice to each character found in the dialog export.

It will then generate the audio files and save them as `{identifier}.mp3`, ready to be used with the auto voice option.

In case you run out of credits (or the generation of files is interrupted for some other reason) the program will detect that there are existing audio files and will give you the option to skip the ones that already exist.

See [here]() for an installation and usage video.

## Installation

1) Download this repo `git clone https://github.com/lugia19/renpyDialogToAudio.git`
2) Open `run.bat`

In case you're not on windows, run.bat just creates a venv and install the requirements from requirements.txt, then runs the script, so you can just do that manually.

In addition, it will also perform a git pull whenever it's run.
