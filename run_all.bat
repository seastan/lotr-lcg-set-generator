cd /D "%~dp0"
if exist env\Scripts\activate.bat call env\Scripts\activate.bat

for /f "usebackq tokens=*" %%i in (`python date.py`) do set date_correct=%%i

python save_remote_logs_path.py
for /f "delims=" %%i in (remote_logs_path) do set log_path=%%i
echo log path: %log_path%\run_all.log

echo %date_correct% %time% batch process started >> "%log_path%\run_all.log"
call run_all_internal.bat >> "%log_path%\run_all.log"
echo %date_correct% %time% batch process finished >> "%log_path%\run_all.log"
exit