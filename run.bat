WHERE git
if %errorlevel% == 0 (
	if exist ".git" (
		git pull "TBA"
	)
)

if not exist "venv" (
	python -m venv venv
	pip install -r requirements.txt
)

call venv\scripts\activate
pip install --upgrade elevenlabslib

python dialogVoiceGenerator.py