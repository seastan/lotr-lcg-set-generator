@echo off
cd /D "%~dp0"
chcp 65001
if exist run_setup.bat call run_setup.bat
if exist env\Scripts\activate.bat call env\Scripts\activate.bat

for /f "usebackq tokens=*" %%i in (`python date.py`) do set date_correct=%%i
for /f "usebackq tokens=*" %%i in (`python ip.py`) do set public_ip=%%i

python save_remote_logs_path.py
for /f "delims=" %%i in (remote_logs_path.txt) do set log_path=%%i
echo log path: %log_path%\run_all.log

echo %date_correct% %time% batch process started (IP: %public_ip%)>> "%log_path%\run_all.log"
call run_all_internal.bat >> "%log_path%\run_all.log"
echo %date_correct% %time% batch process finished>> "%log_path%\run_all.log"

if exist run_cleanup.bat call run_cleanup.bat
exit
