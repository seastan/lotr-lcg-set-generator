if exist env\Scripts\activate.bat call env\Scripts\activate.bat

python save_remote_logs_path.py
for /f %%i in (remote_logs_path) do set log_path=%%i
echo log path: %log_path%\run_all.log

echo %date% %time% batch process started >> %log_path%\run_all.log
call run_all_internal.bat >> %log_path%\run_all.log
echo %date% %time% batch process finished >> %log_path%\run_all.log