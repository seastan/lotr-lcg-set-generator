if exist env\Scripts\activate.bat call env\Scripts\activate.bat
timeout /t 1
python run_before_se.py
timeout /t 1
call strange_eons.ahk
:loop
timeout /t 5
tasklist /fi "ImageName eq strangeeons.exe" /fo csv 2>NUL | find /I "strangeeons.exe">NUL
if "%ERRORLEVEL%"=="0" goto loop
timeout /t 1
python run_after_se.py
timeout /t 60