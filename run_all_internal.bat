for /f "usebackq tokens=*" %%i in (`python date.py`) do set date_correct=%%i

set retry=0

:start
if %retry%==2 (
  echo %date_correct% %time% exiting
  exit /b
)

set /a retry=%retry%+1
echo %date_correct% %time% retry %retry%

echo %date_correct% %time% looking for the running application
wmic process where "commandline like '%%strangeeons.exe%%' and not commandline like '%%wmic%%'" delete

:: tasklist /fi "ImageName eq strangeeons.exe" /fo csv 2>NUL | find /I "strangeeons.exe">NUL
:: if "%ERRORLEVEL%"=="0" (
::   echo %date_correct% %time% ERROR The application is already running
::   exit /b
:: )

echo %date_correct% %time% looking for running autohotkey scripts
wmic process where "commandline like '%%eons.ahk%%' and not commandline like '%%wmic%%'" delete

echo %date_correct% %time% started run_before_se_remote.py
python run_before_se_remote.py
echo %date_correct% %time% finished run_before_se_remote.py

if exist runBeforeSE_STARTED (
  echo %date_correct% %time% ERROR run_before_se_remote.py didn't finish successfully
  goto start
)

if not exist setGenerator_CREATED (
  echo %date_correct% %time% No project created
  goto after
)

echo %date_correct% %time% started eons.ahk
call eons.ahk
echo %date_correct% %time% finished eons.ahk

if not exist makeCards_FINISHED (
  echo %date_correct% %time% ERROR makeCards script didn't finish successfully
  goto start
)

echo %date_correct% %time% waiting until the application is closed
:loop
timeout /t 10
tasklist /fi "ImageName eq strangeeons.exe" /fo csv 2>NUL | find /I "strangeeons.exe">NUL
if "%ERRORLEVEL%"=="0" goto loop

:after
echo %date_correct% %time% started run_after_se_remote.py
python run_after_se_remote.py
echo %date_correct% %time% finished run_after_se_remote.py
