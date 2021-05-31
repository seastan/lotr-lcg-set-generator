tasklist /fi "ImageName eq strangeeons.exe" /fo csv 2>NUL | find /I "strangeeons.exe">NUL
if "%ERRORLEVEL%"=="0" (
  echo %date% %time% ERROR Strange Eons is already running, exiting
  exit /b
)

echo %date% %time% looking for running autohotkey scripts
wmic process where "commandline like '%%strange_eons.ahk%%' and not commandline like '%%wmic%%'" delete

echo %date% %time% started run_before_se_remote.py
python run_before_se_remote.py
echo %date% %time% finished run_before_se_remote.py

if not exist setGenerator_CREATED (
  echo %date% %time% ERROR No Strange Eons project created
) else (
  echo %date% %time% started strange_eons.ahk
  call strange_eons.ahk
  echo %date% %time% finished strange_eons.ahk

  if not exist makeCards_FINISHED (
    echo %date% %time% ERROR makeCards script didn't finish successfully, exiting
    exit /b
  )

  echo %date% %time% waiting until Strange Eons is closed
  :loop
  timeout /t 5
  tasklist /fi "ImageName eq strangeeons.exe" /fo csv 2>NUL | find /I "strangeeons.exe">NUL
  if "%ERRORLEVEL%"=="0" (
    goto loop
  )
)

if not exist runBeforeSE_STARTED (
  echo %date% %time% started run_after_se_remote.py
  python run_after_se_remote.py
  echo %date% %time% finished run_after_se_remote.py
)
