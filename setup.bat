pip install virtualenv
:: Create virtual enviornment
virtualenv venv --python=python3.10
:: Activate virtual enviornment
start venv\Scripts\activate.bat
:: Install requirements under the virtual enviornment
pip install -r requirements.txt

@echo off
echo "Setup complete"
pause "Press enter to exit"