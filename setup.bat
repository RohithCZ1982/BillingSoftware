@echo off
echo Installing dependencies...
"C:\Users\Rohith\AppData\Local\Python\pythoncore-3.12-64\python.exe" -m pip install -r requirements.txt
echo.
echo Initialising database with sample data...
"C:\Users\Rohith\AppData\Local\Python\pythoncore-3.12-64\python.exe" database\sample_data.py
echo.
echo Done! Run "run.bat" to start the application.
pause
