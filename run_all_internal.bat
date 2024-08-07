for /f "usebackq tokens=*" %%i in (`python date.py`) do set date_correct=%%i

set retry=0

:start
if %retry%==3 (
  echo %date_correct% %time% exiting
  exit /b
)

set /a retry=%retry%+1
echo %date_correct% %time% retry %retry%

echo %date_correct% %time% looking for the running application
wmic process where "commandline like '%%strang%%eons.exe%%' and not commandline like '%%wmic%%'" delete

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

set iteration=0
echo %date_correct% %time% waiting until the application is closed

:loop
timeout /t 10
set name="strang"
tasklist /fi "ImageName eq %name%eeons.exe" /fo csv 2>NUL | find /I "eons.exe">NUL
set /a iteration=%iteration%+1

if %iteration%==180 (
  echo %date_correct% %time% ERROR the application didn't close in time
  goto start
)

if "%ERRORLEVEL%"=="0" goto loop

:after
echo %date_correct% %time% started run_after_se_remote.py
python run_after_se_remote.py
echo %date_correct% %time% finished run_after_se_remote.py
