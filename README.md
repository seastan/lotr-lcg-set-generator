**Introduction**

This is a private tool not intended for use by anyone else.  Don't expect sufficient documentation or
any kind of support.

**Setup**

To generate final image outputs, you must run this workflow on a Windows platform because each platform
renders the fonts differently.

1. Clone this repo to a new local folder.  The easiest way is to click `Code` and then `Download ZIP`.
At the same time, the preferable way is to use Git.

    You can install the Git client from https://git-scm.com/downloads
    (default settings should be fine).  On GitHub UI click `Code`, then click `HTTPS` and copy the URL.
    Run `Git CMD`, navigate to the folder, and run the following command (don't forget the period at the end):

    ```
    git clone <copied URL> .
    ```

    For example:

    ```
    git clone https://github.com/seastan/lotr-lcg-set-generator.git .
    ```

    Later, when you want to update the code, run `Git CMD`, navigate to the folder, and run the following command:

    ```
    git pull
    ```

    If you prefer a UI interface, instead of `Git CMD` you may also use `GitHub Desktop` (https://desktop.github.com).
    In that case, on GitHub UI click `Code`, then click `Open with Github Desktop`.

2. Make sure there is a spreadsheet on Google Sheets (most likely, it already exists).

    If it doesn't exist yet (that means you are starting a new project from scratch),
    upload `Spreadsheet/spreadsheet.xlsx` from this repo, click `Save as Google Sheets`,
    click `Share` and `Change to anyone with the link`.  Click `Extensions -> Apps Script` and upload the content
    of `Spreadsheet/Code.gs`.  After that, re-run `=SHEETS()` function from `A1` cell of the first `-` tab.
    Add all the sets and the card data.

3. Add the folder with the artwork to your Google Drive to be able to sync it locally.
Open the folder in the browser, right-click on the folder name, then click `Add shortcut to Drive`.
Choose `My Drive` and click `Add Shortcut`.

    If it doesn't exist yet (that means you are starting a new project from scratch), create this folder locally.
    Make sure that you don't reuse an existing folder from the downloaded repo.
    It should have the following structure:

    ```
    <set ID>/
    <set ID>/<card ID>_<"A"|"B"|"Top"|"Bottom">_<card name and artist, format is not strict>.<"jpg" or "png">
    <set ID>/custom/
    <set ID>/custom/<custom image>
    custom/
    custom/<custom image>
    generated/
    generated/<generated lightweight card image>
    icons/
    icons/<icon image>
    _Keep/
    _Keep/<card ID>/
    _Keep/<card ID>/<image ID>_<artist>.<"jpg" or "png">
    _Scratch/
    _Scratch/<backup image>
    ```

    For example:

    ```
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/53dcedb3-3640-4655-a150-9d0dd534a126_A_Reclaim_the_Beacon_Artist_Jan_Pospisil.jpg
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/53dcedb3-3640-4655-a150-9d0dd534a126_B_Defend_the_Beacon_Artist_Skvor.jpg
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/9a677840-6c2d-4603-b2bd-c39464663913_A_Squire_of_the_Mark_Artist_Ekaterina_Burmak.png
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/custom/
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/custom/Encounter-Icons-Ambush-at-Erelas.png
    custom/
    custom/Do-Not-Read-the-Following.png
    generated/
    generated/e904fc83-7bb9-4868-8d80-60c89ade0ce2.jpg
    icons/
    icons/Vafthrudnir-Encounter-Set-01.png
    _Keep/
    _Keep/53dcedb3-3640-4655-a150-9d0dd534a126/d683951a-e2a9-4e6f-81aa-2943ff6c0a31_John_Howe.png
    _Scratch/
    _Scratch/untitled.png
    ```

    Make sure that top-level folders `custom`, `generated`, `icons`, `_Keep`, and `_Scratch` exist, even if they are empty.
    If you are starting a new project from scratch, copy all images from `imagesCustom` and `imagesIcons` folders in the root
    of this repo to `custom` and `icons` folders in the root of this folder.

4. If you are using the artwork from Google Drive, make sure that the Google Drive application is installed (install it if needed).
If the artwork folder is a shortcut, click on the shortcut and copy the actual path to the virtual folder (it might look like
`G:\.shortcut-targets-by-id\1FY4jVevupiOL48eYOPCPAWqVZq3pQKvO\<folder name>`.  Use that path in the configuration file
described below.  Right-click on the folder, then click `Offline access` and `Available offline`.

If you plan to use the latest stable data when a sanity check fails, create a shortcut for the stable data folder on Google Drive
and use its local path in the configuration (repeat the instruction above).

5. If you plan to upload to Google Drive any card outputs or log files, you might need to create shortcuts for more
existing Google Drive folders and use their local paths in the configuration (repeat the instruction above).

6. Install the tool and the plugin.  Follow these steps:

  - Make sure that `Times New Roman` font is installed.  If you have a Mac or Linux, it may be not installed by default.
  - Install the tool, `Build 3970`.  Please note that the latest version from the site may not work as expected.  Use the following links:
    - Windows (64-bit): https://drive.google.com/file/d/1tqzVeZB27MC_EaOwKXipBODbRL3wBdSr/view?usp=sharing
    - Windows (32-bit): https://drive.google.com/file/d/1QbruPIOyioZ4MWpLF1YUMaAgnGq8Ch_Y/view?usp=sharing
    - Mac: https://drive.google.com/file/d/1QcDhm0Bv9de81DNnp0E4obMGtVBtcCnV/view?usp=sharing
    - Linux: https://drive.google.com/file/d/1QeTjzV4OWdvaEP8oGGX9kIeflGdtlrzH/view?usp=sharing
  - Run the tool and install `The Lord of the Rings LCG` plugin.
  - Click `Edit` -> `Preferences` -> `Language`.  Make sure that "English-United States" is chosen for both `Game Language` and `User Interface Language`.
    Click `Drawing`.  Make sure that `Text Fitting Methods` is set to `Reduce Line Spacing and Shrink Text`.  Don't change any other preferences.
  - If you have any custom plugin files, do the following: Go to the plugins folder (run the tool, then click
    `Toolbox` -> `Manage Plug-ins` -> `Open Plug-in Folder`), close the tool, delete all files, whose names start with `TheLordOfTheRingsLCG`,
    and copy your custom `.seext` files instead of them.

7. Install the latest GIMP version from https://www.gimp.org/downloads/.  If for some reason it doesn't work as expected,
try to install version 2.10.20.

8. Open GIMP, go to `Edit` -> `Preferences` -> `Folders` -> `Plug-ins`, add `GIMP` folder
from this repo, click `OK`, and then close GIMP.

9. Install ImageMagick 7.0.10-28 (download Windows version from https://drive.google.com/file/d/1toCZd4xaYU2ToV-_jc3xXmQW1rJcxmRK/view?usp=sharing,
for other platforms look at https://download.imagemagick.org/ImageMagick/download/releases/).

10. Download `USWebCoatedSWOP.icc` from
https://github.com/cjw-network/cjwpublish1411/blob/master/vendor/imagine/imagine/lib/Imagine/resources/Adobe/CMYK/USWebCoatedSWOP.icc
into the root folder of this repo.

11. Install AutoHotkey from https://autohotkey.com/download/.

12. Install the latest Python 3 version (see https://www.python.org/downloads/).  The minimum version that was tested is 3.7.
Optionally, install VirtualEnv (see https://help.dreamhost.com/hc/en-us/articles/115000695551-Installing-and-using-virtualenv-with-Python-3
for details).

13. Go to the root folder of this repo and follow the steps below.  All commands should be run in CLI, for example, `cmd` (Windows)
or `bash` (Mac/Linux).  To navigate to the right folder inside your CLI you can use `cd <folder>` command
(for example, `cd Documents\lotr-lcg-set-generator`).

  - [skip this step, if you don't use VirtualEnv] `virtualenv env --python=python3.9` (replace `3.9` with your actual Python version)
  - [skip this step, if you don't use VirtualEnv] `env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac/Linux)
  - `pip install -r requirements.txt`

    If for debugging purposes you plan to use Jupyter notebook, additionally run:

  - `pip install jupyter`

14. Create `configuration.yaml`: copy `configuration.default.yaml` to `configuration.yaml` and set the following values:

  - `sheet_gdid`: Google Sheets ID of the cards spreadsheet
  - `artwork_path`: local path to the artwork folder (don't use for that purpose any existing folder in this repo)
  - `stable_data_path`: local path to the stable data folder
  - `gimp_console_path`: path to GIMP console executable
  - `magick_path`: path to ImageMagick executable
  - `dragncards_id_rsa_path`: path to id_rsa key to upload files to DragnCards (may be empty)
  - `remote_logs_path`: path to remote logs folder (may be empty)
  - `octgn_set_xml_destination_path`: path to OCTGN `set.xml` destination folder (may be empty)
  - `octgn_set_xml_scratch_destination_path`: path to OCTGN `set.xml` scratch destination folder (may be empty)
  - `octgn_o8d_destination_path`: path to OCTGN `.o8d` destination folder (may be empty)
  - `octgn_o8d_scratch_destination_path`: path to OCTGN `.o8d` scratch destination folder (may be empty)
  - `octgn_image_destination_path`: path to OCTGN image destination folder (may be empty)
  - `db_destination_path`: path to DB destination folder (may be empty)
  - `tts_destination_path`: path to TTS destination folder (may be empty)
  - `dragncards_remote_image_path`: remote DragnCards path to image folder
  - `dragncards_remote_json_path`: remote DragnCards 1.0 path to set JSON folder
  - `dragncards_remote_tsv_path`: remote DragnCards 2.0 path to set TSV folder
  - `dragncards_remote_deck_path`: remote DragnCards 1.0 path to deck O8D folder
  - `dragncards_remote_deck_json_path`: remote DragnCards 2.0 path to deck JSON folder
  - `reprocess_all`: whether to reprocess all cards (`true`) or update only the cards, changed since the previous script run (`false`)
  - `reprocess_all_on_error`: whether to reprocess all cards even when reprocess_all=false if the previous script run didn't succeed (true or false)
  - `selected_only`: process only "selected" rows (true or false)
  - `exit_if_no_spreadsheet_changes`: stop processing if there are no spreadsheet changes (true or false)
  - `run_sanity_check_for_all_sets`: run sanity check for all sets (true or false)
  - `parallelism`: number of parallel processes to use (`default` means `cpu_count() - 1`, but not more than 4)
  - `stable_data_user`: how to use the stable data: "none" (don't use stable data), "reader" (read the latest stable data when sanity check failed), "writer" (write the stable data when sanity check passed)
  - `verify_drive_timestamp`: verify whether Google Drive is up to date or not (true or false)
  - `ignore_ignore_flags`: ignore IgnoreName and IgnoreRules flags (true or false)
  - `set_ids`: list of set IDs to work on (you can use `all` and `all_scratch` aliases to select all non-scratch and all scratch sets automatically)
  - `ignore_set_ids`: list of set IDs to ignore
  - `set_ids_octgn_image_destination`: list of set IDs to copy to OCTGN image destination
  - `octgn_set_xml`: creating `set.xml` files for OCTGN (true or false)
  - `octgn_o8d`: creating O8D and JSON files for OCTGN and DragnCards (true or false)
  - `ringsdb_csv`: creating CSV files for RingsDB (true or false)
  - `dragncards_json`: creating JSON and TSV files for DragnCards (true or false)
  - `hallofbeorn_json`: creating JSON files for Hall of Beorn (true or false)
  - `frenchdb_csv`: creating CSV files for the French database sda.cgbuilder.fr (true or false)
  - `spanishdb_csv`: creating CSV files for the Spanish database susurrosdelbosqueviejo.com (true or false)
  - `renderer_artwork`: creating artwork for DragnCards proxy images (true or false)
  - `renderer`: creating DragnCards proxy images (true or false)
  - `upload_dragncards`: uploading pixel-perfect images to DragnCards (true or false)
  - `upload_dragncards_lightweight`: uploading lightweight outputs to DragnCards (true or false)
  - `dragncards_hostname`: DragnCards hostname: `username@hostname` (may be empty)
  - `update_ringsdb`: updating ringsdb.com (true or false)
  - `ringsdb_url`: ringsdb.com URL (may be empty)
  - `ringsdb_sessionid`: ringsdb.com session ID: `<PHPSESSID>|<REMEMBERME>` (may be empty)
  - `outputs`: list of image outputs for each language (if you added or uncommented new outputs, you also need to set `reprocess_all` to `true`)

For debugging purposes, you may add an additional value:

  - `offline_mode`: use a cached spreadsheet when possible (true or false)

See `configuration.release.yaml` for a configuration example.

**Usage**

To run the workflow, go to the root folder of this repo and follow these steps:

- [skip this step, if you don't use VirtualEnv] `env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac/Linux).
- Make sure that the tool is closed.
- `python run_before_se.py`.
- Pay attention to possible errors in the script output.
- Open `setGenerator.seproject` and run `makeCards` script by double-clicking it.
  Once completed, close the program and wait until it finishes packing the project.
- `python run_after_se.py`.
- Pay attention to possible errors in the script output.

For debugging purposes, you can also run the steps above using the Jupyter notebook (it doesn't use any parallelism):

- [skip this step, if you don't use VirtualEnv] `env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac/Linux)
- `jupyter notebook`
- Open `setGenerator.ipynb` in the browser.

To generate only a subset of cards (produce separate artifacts for each set):

- Set `selected_only: true` in `configuration.yaml`.
- Uncomment all the needed sets in `configuration.yaml`.
- In the spreadsheet, set `Selected` column to 1 for all the needed cards.

To generate only a subset of cards (produce one artifact regardless of the sets):

- Set `selected_only: true` in `configuration.yaml`.
- In the spreadsheet, on the `Sets` tab add a new set like `Selected Cards`.
- Add that new set to `configuration.yaml` and comment out any other sets.
- In the spreadsheet, set `Selected` column to the ID of that new set for all the needed cards.
- In the artwork folder, temporarily create a new folder named the new set ID and copy all images and subfolders
  from the folders with the set IDs that you refer to in your selected cards (there should be no naming conflicts between files
  from the different folders).  After you finish generating the cards, you can safely delete this folder.
  Also, when running the scripts you can ignore any `Unused image detected` errors.

**Automatic Pipeline**

To run the workflow as one script, run:

- `run_all.bat`

Please note, this script is for the Windows platform only.  It uses AutoHotkey to emulate UI commands
and is not 100% reliable (it may be stuck on the manual step).  To minimize the risks:

- Make sure the tool window was maximized when you closed it.
- Make sure the screen is not locked (and doesn't lock automatically).
- If the script starts, don't touch the keyboard or mouse.

If you need to perform any additional actions before and/or after the script starts (like
restarting Google Drive), you may create two additional batch scripts with your custom code:

- `run_setup.bat`
- `run_cleanup.bat`

They will be called inside `run_all.bat` automatically.  See `run_setup.bat.example`.

Also, see `configuration.nightly.yaml` for a configuration example.

If you want to set up a Windows cron job, do the following:

- Run `Task Scheduler`.
- Click `Create Task`.
- Set `Name`.
- Click `Triggers` -> `New`.
- Set up a schedule and click `OK`.
- Click `Actions` -> `New`.
- Click `Browse...`, choose `run_all.bat`, and click `OK`.
- Click `OK`.

**Cron Job Pipeline**

Of the Setup steps described above, you need only these:

1. Clone this repo to a new local folder:

    ```
    git clone https://github.com/seastan/lotr-lcg-set-generator.git .
    ```

2. Install the latest Python 3 version (if it's not yet installed, the minimum supported version is 3.7).

3. Create `configuration.yaml`.  Use `configuration.cron.yaml` as a template.  Replace `/home/user/Drive/`
with an actual path to a local `Drive` folder (create a new folder either in the root folder of this repo
or somewhere else).  It should have the following structure:

    ```
    CardImages/
    CardImagesTemp/
    LinksBackup/
    Logs/
    Playtesting/
    Playtesting/OCTGN Files/
    Playtesting/OCTGN Files/Encounter Decks/
    Playtesting/OCTGN Files/Scratch Encounter Decks/
    Playtesting/OCTGN Files/Scratch Set Folders/
    Playtesting/OCTGN Files/Set Folders/
    ```

Additional steps:

1. Install all dependencies:

  - `pip install -r requirements.txt`
  - `pip install discord.py==1.7.3 aiohttp`
  - Patch discord.py package: find the folder where it's installed (something like `/usr/local/lib/python<version of Python>/dist-packages/discord`) and run: `sudo cp _discord_1_7_3_patch/* <discord.py folder>/`.
  - `sudo apt-get install nodejs npm imagemagick`
  - Download the latest stable `wkhtmltopdf` package for your platform from https://wkhtmltopdf.org/downloads.html and run `sudo apt-get install <absolute path to the package file>`.
  - `cd Renderer/; npm install fast-xml-parser he; cd ..`

2. Create `discord.yaml` (see `discord.default.yaml`).

3. Create `mpc_monitor.json` (see `mpc_monitor.default.json`), `mpc_monitor_cookies.json` (see `mpc_monitor_cookies.default.json`),
`ringsdb_prod_cookies.json` (see `ringsdb_prod_cookies.default.json`), `scheduled_backup.json` (see `scheduled_backup.default.json`) and
`mail.yaml` (see `mail.default.json`).

4. Setup rclone:

  - `curl https://rclone.org/install.sh | sudo bash`
  - `rclone config`

    You will need to set up the following remotes:

  - `ALePCardImages` (points to `CardImages`)
  - `ALePCron` (points to `Cron`)
  - `ALePGeneratedImages` (points to `CardImages/generated`)
  - `ALePIcons` (points to `CardImages/icons`)
  - `ALePLinksBackup` (points to `Links Backup`)
  - `ALePLogs` (points to `Logs`)
  - `ALePOCTGN` (points to `Playtesting/OCTGN Files`)
  - `ALePRenderedImages` (points to `RenderedImages`)
  - `ALePStableData` (points to `StableData`)

5. In the root folder of this repo create `id_rsa` to upload files to DragnCards.

6. Setup crons:

  - `*/5 * * * *   <path>/check_cron.sh >> <path>/cron.log 2>&1`
  - `* * * * *     <path>/check_discord_bot.sh >> <path>/cron.log 2>&1`
  - `* * * * *     <path>/check_internet_state.sh >> <path>/cron.log 2>&1`
  - `* * * * *     <path>/check_mail.sh >> <path>/cron.log 2>&1`
  - `*/10 * * * *  <path>/check_mpc_monitor.sh >> <path>/cron.log 2>&1`
  - `19 * * * *    <path>/check_playtesting_sets.sh >> <path>/cron.log 2>&1`
  - `9 * * * *     <path>/check_ringsdb_decks.sh >> <path>/cron.log 2>&1`
  - `* * * * *     <path>/check_run_before_se_service.sh >> <path>/cron.log 2>&1`
  - `7 1 * * *     <path>/configuration_backup.sh "<path to a local configuration backup folder>" >> <path>/cron.log 2>&1`
  - `5 11 * * *    <path>/download_ringsdb_stat.sh >> <path>/cron.log 2>&1`
  - `* * * * *     <path>/env_health_check.sh >> <path>/cron.log 2>&1`
  - `*/2 * * * *   <path>/monitor_discord_changes.sh >> <path>/cron.log 2>&1`
  - `15 0 * * *    <path>/monitor_discord_log.sh >> <path>/cron.log 2>&1`
  - `29 4 * * *    <path>/monitor_images_upload.sh >> <path>/cron.log 2>&1`
  - `36 8 * * *    <path>/monitor_remote_pipeline.sh >> <path>/cron.log 2>&1`
  - `36 8 * * *    <path>/monitor_wordpress_site.sh >> <path>/cron.log 2>&1`
  - `36 7 * * *    <path>/monitor_mpc_url_format.sh >> <path>/cron.log 2>&1`
  - `0 1 * * *     <path>/monitor_wordpress_token.sh >> <path>/cron.log 2>&1`
  - `17 7 1 */2 *  <path>/mpc_backup.sh >> <path>/cron.log 2>&1`
  - `*/5 * * * *   <path>/mpc_monitor.sh >> <path>/cron.log 2>&1`
  - `17 6 * * 0    <path>/mpc_refresh.sh >> <path>/cron.log 2>&1`
  - `7 0 * * *     <path>/rclone_backup.sh "<local Drive/Playtesting/OCTGN Files path>" >> <path>/cron.log 2>&1`
  - `12,42 * * * * <path>/rclone_data_remotely.sh >> <path>/cron.log 2>&1`
  - `22,52 * * * * <path>/rclone_renderer.sh >> <path>/cron.log 2>&1`
  - `0 8 * * 1     <path>/remind_backup.sh >> <path>/cron.log 2>&1`
  - `5 8 1 * *     <path>/remind_monthly.sh >> <path>/cron.log 2>&1`
  - `0 12 * * *    <path>/remote_player_cards_stat_monitor.sh >> <path>/cron.log 2>&1`
  - `19 8 * * *    <path>/scheduled_backup.sh "<local Drive/LinksBackup path>" >> <path>/cron.log 2>&1`
  - `0,30 * * * *  <path>/utc_timestamp.sh >> <path>/cron.log 2>&1`

    Replace `<path>` with the absolute path to the root folder of this repo.  `cron.log` may be located either in the root folder
    or in some external folder (if you already have other crons).  Set `<path to a local configuration backup folder>`
    to some backup folder outside of the root folder.

7. Download `Vafthrudnir` font from https://www.wfonts.com/font/vafthrudnir, extract the archive, and
put `VAFTHRUD.TTF` into `Renderer/Fonts` folder.  Find a `ttf` file for the `Times New Roman` font (you may find it in
`c:\Windows\Fonts` folder on a Windows machine or download it from the Internet) and put it into `Renderer/Fonts`
folder as `times.ttf`.

If you want to manually restart the scripts, run:

- `./restart_discord_bot.sh`
- `./restart_mail.sh`
- `./restart_run_before_se_service.sh`

If you want to migrate the pipeline to a different host, do the following steps:

1. Set up the pipeline on the new host, but comment out all crons.  You might want to adjust the hours column in the crontab
according to the new timezone.  Also, you may copy `id_rsa` and configuration files from the old host and only apply
changes where needed (for example, different local paths).  Instead of configuring `rclone` from scratch,
you may copy its configuration file from the old host (run `rclone config file` to find its location on each host).

2. Comment out all crons on the old host and make sure all running crons have been finished
(you may just wait for up to 5 minutes).

3. Run `tail -f run_before_se.log` on the old host.  After another iteration has been finished,
kill `python3 run_before_se_service.py` process (use `ps aux | grep run_before_se` and `kill <process id>` commands).

4. Wait until no files remain in `Discord/Changes`, `Discord/Images`, and `Discord/Temp` folders on the old host and kill
`python3 discord_bot.py` process (use `ps aux | grep discord` and `kill <process id>` commands).

5. Run `./rclone_data_remotely.sh` on the old host.

6. Copy `mpc_monitor_cookies.json`, `ringsdb_prod_cookies.json` and `ringsdb_test_cookies.json` to the new host.

7. On the new host, run `./rclone_data_locally.sh`.

8. On the new host, delete `env_health_check.txt` if it exists.

9. On the new host, uncomment all crons.

If you want to add a new MakePlayingCards deck to monitoring, run:

- `./mpc_add.sh "<deck name>"`

**Outputs**

The scripts will generate the following outputs:

- `Output/DB/<set name>.<language>/`: 300 dpi PNG images for general purposes (including TTS).
- `Output/DragnCards/<set name>/<set name>.json`: a JSON output file for DragnCards.
- `Output/DragnCards/<set name>/<set name>.tsv`: a TSV output file for DragnCards.
- `Output/DragnCardsHQ/<set name>/`: 480 dpi JPG images for DragnCards.
- `Output/FrenchDB/<set name>/`: CSV files for French database sda.cgbuilder.fr.
- `Output/FrenchDBImages/<set name>.<language>/`: 300 dpi PNG images for French database (the same as `Output/DB`, but differently named).
- `Output/GenericPNG/<set name>.<language>/`: a `7z` archive of generic 800 dpi PNG images with bleed margins.
- `Output/GenericPNGPDF/<set name>.<language>/`: `7z` archives of PDF files in `A4` and `letter` format (800 dpi PNG images with bleed margins).
- `Output/HallOfBeorn/<set name>.<language>/<set name>.json`: an output file for Hall of Beorn.
- `Output/HallOfBeornImages/<set name>.<language>/`: 300 dpi PNG images for Hall of Beorn (the same as `Output/DB`, but differently named).
- `Output/MakePlayingCards/<set name>.<language>/`: a `7z` archive of 800 dpi PNG images with bleed margins to be printed on MakePlayingCards.com.
- `Output/MBPrint/<set name>.<language>/`: a `7z` archive of 800 dpi CMYK (U.S. Web Coated (SWOP) v2) JPG images with bleed margins to be printed
  on MBPrint.pl or some other printing service.
- `Output/MBPrintPDF/<set name>.<language>/`: a `7z` archive of a PDF file to be printed on MBPrint.pl (800 dpi CMYK (U.S. Web Coated (SWOP) v2)
  JPG images with bleed margins).
- `Output/OCTGN/<set name>/<octgn id>/set.xml`: an output file for OCTGN.
- `Output/OCTGNDecks/<set name>/<deck name>.json`: quest decks for DragnCards.
- `Output/OCTGNDecks/<set name>/<deck name>.o8d`: quest decks for OCTGN and DragnCards.
- `Output/OCTGNImages/<set name>.<language>/<set name>.<language>.o8c`: image packs for OCTGN and DragnCards (600x429 JPG images).
- `Output/PDF/<set name>.<language>/`: PDF files in `A4` and `letter` format for home printing (300 dpi PNG images with bleed margins).
- `Output/PreviewImages/<set name>.<language>/`: 600x429 JPG images for preview purposes.
- `Output/RingsDB/<set name>/<set name>.csv`: an output file for RIngsDB.
- `Output/RingsDBImages/<set name>/`: 300 dpi PNG images for RingsDB (the same as `Output/DB`, but player cards only and differently named).
- `Output/RulesPDF/<set name>.<language>/Rules.<set name>.<language>.pdf`: a PDF file with all Rules pages (800 dpi JPG images).
- `Output/SpanishDB/<set name>/`: CSV files for Spanish database susurrosdelbosqueviejo.com.
- `Output/SpanishDBImages/<set name>.<language>/`: 300 dpi PNG images for Spanish database (the same as `Output/DB`, but differently named).
- `Output/TTS/<set name>.<language>/`: 300 dpi JPG image sheets for TTS.

Please note that `Output/DB`, `Output/HallOfBeornImages`, `Output/PreviewImages`, `Output/RingsDBImages` (for English language only),
`Output/FrenchDBImages` (for French language only), and `Output/SpanishDBImages` (for Spanish language only)
are generated when `db` output is enabled in the configuration.

When `tts` output is enabled in the configuration, `octgn_o8d`, and `db` outputs become enabled automatically.

**Supported Tags**

Please note that all tags are case-sensitive.

- `[center]` ... `[/center]`: center alignment
- `[right]` ... `[/right]`: right alignment
- `[b]` ... `[/b]`: bold text
- `[i]` ... `[/i]`: italic text
- `[bi]` ... `[/bi]` or `{` ... `}`: bold + italic text
- `[u]` ... `[/u]`: underlined text
- `[strike]` ... `[/strike]`: strikethrough text
- `[red]` ... `[/red]`: red (#8B1C23) text
- `[lotr X]` ... `[/lotr]`: Vafthrudnir font + text size X (X may be float)
- `[lotrheader X]` ... `[/lotrheader]`: Lord of the Headers font + text size X (X may be float)
- `[size X]` ... `[/size]`: text size X (X may be float)
- `[defaultsize X]`: put it at the beginning of a field, to set default text size X (X may be float)
- `[img PATH]`: insert image from PATH (PATH may start either with "custom/" or "icons/")
- `[img PATH Xin]`: insert image from PATH and set its width to X inches
- `[img PATH Xin Yin]`: insert image from PATH and set its width to X inches and its height to Y inches
- `[space]`: horizontal spacing
- `[vspace]`: vertical spacing
- `[tab]`: tab symbol
- `[nobr]`: non-breakable space
- `[br]`: doesn't do anything, use this tag before the actual linebreak to emphasize that the linebreak was intentional
- `[lsb]`: [
- `[rsb]`: ]
- `[lfb]`: {
- `[rfb]`: }
- `[lquot]`: unmatched left quote
- `[rquot]`: unmatched right quote
- `[lfquot]`: unmatched French left quote
- `[rfquot]`: unmatched French right quote
- `[quot]`: "
- `[apos]`: '
- `[hyphen]`: -
- `[inline]`: put it at the end of the `Keywords` field, to place the keywords on the same line as the first line of the text
- `[split]`: split the text between different regions (only for `Cave` card type)
- `[name]`: this card's name (never hardcode the name itself)
- `[[Name]]`: reference to a different card name (allows to apply a check for unknown names)
- `{Trait}`: an alias for `[bi]Trait[/bi]`
- `--`: en dash
- `---`: em dash

Icons:

- `[unique]`
- `[threat]`
- `[attack]`
- `[defense]`
- `[willpower]`
- `[leadership]`
- `[lore]`
- `[spirit]`
- `[tactics]`
- `[baggins]`
- `[fellowship]`
- `[sunny]`
- `[cloudy]`
- `[rainy]`
- `[stormy]`
- `[sailing]`
- `[eos]`: Eye of Sauron
- `[pp]`: per player

**Card Types & Spheres**

List of available card types:

- `Ally`
- `Attachment`
- `Campaign`
- `Contract`
- `Encounter Side Quest` (alias: `Side Quest`)
- `Enemy`
- `Event`
- `Full Art Landscape`
- `Full Art Portrait`
- `Hero`
- `Location`
- `Nightmare`
- `Objective`
- `Objective Ally`
- `Objective Hero`
- `Objective Location`
- `Player Objective`
- `Player Side Quest`
- `Presentation`
- `Quest`
- `Rules`
- `Ship Enemy`
- `Ship Objective`
- `Treachery`
- `Treasure`

List of available sphere values:

- `Baggins`
- `Fellowship`
- `Leadership`
- `Lore`
- `Neutral`
- `Spirit`
- `Tactics`
- `Boon`
- `BoonLeadership`
- `BoonLore`
- `BoonSpirit`
- `BoonTactics`
- `Burden`
- `Nightmare`
- `Back` (`Rules` only)
- `Cave` (`Encounter Side Quest` only)
- `NoIcon` (`Objective` only)
- `Ring` (`Objective` only)
- `NoProgress` (`Encounter Side Quest` only)
- `NoStat` (`Enemy` only)
- `Region` (`Encounter Side Quest` only)
- `Setup` (`Campaign` only)
- `SmallTextArea` (`Encounter Side Quest` only)
- `Upgraded` (`Ship Objective` only)
- `Blue` (`Presentation` only)
- `Green` (`Presentation` only)
- `Purple` (`Presentation` only)
- `Red` (`Presentation` only)
- `Brown` (`Presentation` only)
- `Yellow` (`Presentation` only)
- `BlueNightmare` (`Presentation` only)
- `GreenNightmare` (`Presentation` only)
- `PurpleNightmare` (`Presentation` only)
- `RedNightmare` (`Presentation` only)
- `BrownNightmare` (`Presentation` only)
- `YellowNightmare` (`Presentation` only)

**Flags**

- `AdditionalCopies`
- `IgnoreName`
- `IgnoreRules`
- `NoArtist`
- `NoCopyright`
- `NoTraits`
- `Promo` (`Hero` only)
- `Star`
- `BlueRing`
- `GreenRing`
- `RedRing`

**Portrait Shadows**

- `Black`
- `PortraitTint` (`Quest` Side A only)

**Deck Rules**

OCTGN/DragnCards `.o8d` and DragnCards `.json` deck files are generated automatically for each scenario detected
on `Quest` and `Nightmare` cards.  By default, the deck includes all cards, that share both the set
and encounter set from the "parent" `Quest` or `Nightmare` card (including encounter sets from
`Additional Encounter Sets` column).  All `Quest`, `Nightmare`, and `Campaign` cards are put into
`Quest` section, all `Rules` cards are put into `Setup` section, and all encounter cards are put into
`Encounter` section.  The filename of the deck is the same as `Adventure` value (`Quest` cards) or
`Name` value (`Nightmare` cards) with all spaces replaced with `-`.  The easy mode version is generated
automatically if any card included in the deck has a different quantity for the normal and easy modes.

To adjust the deck, you need to describe the rules in `Deck Rules` column (for a corresponding `Quest`
or `Nightmare` card).  The rules are separated by a line break.  If you want to create several decks
for the same scenario (for example, a normal and a campaign deck), describe the rules for each of the decks
and separate them using an additional empty line.  For example:

```
[rule 1 for deck 1]
[rule 2 for deck 1]

[rule 1 for deck 2]
[rule 2 for deck 2]
[rule 3 for deck 2]
```

Each rule is a key-value pair, separated by `:`.  For example:

```
Prefix: QA1.5
```

If you want to set a list of values, separate them by `;`.  For example:

```
Setup: Saruman; Grima; Brandywine Gate
```

Below is a list of all supported rules:

- `Prefix`: A **mandatory** scenario prefix.  It must start with:
  `<either "Q" (normal mode) or "N" (nightmare mode)><two capital letters and/or numbers>.<one or two numbers><end of string or dash>`.
  For example, `Prefix: Q0B.19-Standalone` will result in a filename like `Q0B.19-Standalone-The-Scouring-of-the-Shire.o8d`.
- `Sets`: Additional sets to be included.  For example: `Sets: The Road Darkens`.
- `Encounter Sets`: Additional encounter sets to be included.  For example:
  `Encounter Sets: Journey in the Dark`.
- `External XML`: Links to external `set.xml` files (if those cards are not in the spreadsheet).
  For example: `External XML: https://raw.githubusercontent.com/seastan/Lord-of-the-Rings/master/o8g/Sets/The%20Road%20Darkens/set.xml`.
- `Remove`: List of filters to select cards that need to be removed from the deck.  For example:
  `Remove: Type:Campaign` (remove any cards with `Campaign` type from the normal deck).
- `Second Quest Deck`, `Special`, `Second Special`, `Setup`, `Staging Setup`, and `Active Setup`:
  List of filters to select cards for that OCTGN section.  For example: `Setup: Saruman; Grima; Brandywine Gate`.
- `Main Quest`, `Extra1`, `Extra2`, `Extra3`, `Extra4`, `Extra5`, `Extra6`, `Extra7`, and `Extra8`:
  List of filters to select cards for that DragnCards-only section.  For example:
  `Main Quest: Drive Them Away`.  Please note that all `Main Quest` cards are put into `Quest` OCTGN section and
  all `ExtraN` cards are put into either `Quest` or `Setup` OCTGN sections, depending on the card type.
- `Player`: List of filters to select cards for `Hero`, `Ally`, `Attachment`, `Event`, and `Side Quest`
  sections (exact section is defined automatically).  For example: `Player: Frodo Baggins`.

Order of rules is important.  For example:

```
Setup: Grievous Wound
Remove: Set:The Road Darkens
```

First, we add `Grievous Wound` to `Setup` section.  After that, we remove all other cards from
`The Road Darkens` set.

Below is a list of all supported filters:

- `[encounter set]` - all cards from a particular encounter set.  For example: `[Caves Map]`.
- `Set:card set` - all cards from a particular set.  For example: `Set:The Road Darkens`.
- `Type:card type` - all cards with a particular type.  For example: `Type:Enemy`.
- `Sphere:card sphere` - all cards with a particular sphere.  For example: `Sphere:Boon`.
- `Trait:card trait` - all cards with a particular trait.  For example: `Trait:Rohan`.
- `Keyword:keyword` - all cards with a particular keyword.  For example: `Keyword:Safe`.
- `Unique:1` - all unique cards.
- `card name` - all copies of a card with a particular name.  For example: `Shores of Anduin`.
- `card GUID` - all copies of a card with a particular GUID.  For example: `de8c3087-3a5d-424c-b137-fb548beb659e`.

You can filter by an empty value.  For example: `Sphere:` (all non-Nightmare cards).

You can combine several filters with `&`.  For example: `[The Aldburg Plot] & Trait:Suspicious`
means all cards with `Suspicious` trait from `The Aldburg Plot` encounter set.

Instead of selecting all copies of a card, you can specify the exact number.  For example:
`4 One-feather Shirriff` means 4 copies of `One-feather Shirriff` and `1 Type:Enemy`
means one copy of each different enemy.

A few more examples:

```
Prefix: Q0B.19-Standalone
Remove: Type:Campaign
Special: Trait:Sharkey & Type:Treachery
Setup: Saruman; Grima; Brandywine Gate; Type:Side Quest; 4 One-feather Shirriff
Player: Frodo Baggins

Prefix: Q0C.19-Campaign
External XML: https://raw.githubusercontent.com/seastan/Lord-of-the-Rings/master/o8g/Sets/The%20Road%20Darkens/set.xml
Sets: The Road Darkens
Encounter Sets: Journey in the Dark
Setup: Grievous Wound
Remove: Set:The Road Darkens
Special: Trait:Sharkey & Type:Treachery
Setup: Saruman; Grima; Brandywine Gate; Type:Side Quest; 4 One-feather Shirriff; Sphere:Boon
Player: Frodo Baggins
```

```
Prefix: N01.5-Nightmare
External XML: https://raw.githubusercontent.com/seastan/Lord-of-the-Rings/master/o8g/Sets/Core%20Set/set.xml; https://raw.githubusercontent.com/seastan/Lord-of-the-Rings/master/o8g/Sets/Conflict%20at%20the%20Carrock/set.xml; https://raw.githubusercontent.com/seastan/Lord-of-the-Rings/master/o8g/Sets/Shadows%20of%20Mirkwood%20-%20Nightmare/set.xml
Sets: Core Set; Conflict at the Carrock; Shadows of Mirkwood - Nightmare
Encounter Sets: Journey Down the Anduin; Wilderlands; Conflict at the Carrock; Conflict at the Carrock - Nightmare
Remove: [Journey Down the Anduin] & Type:Quest; Grimbeorn the Old; [Conflict at the Carrock] & Louis; [Conflict at the Carrock] & Morris; [Conflict at the Carrock] & Stuart; [Conflict at the Carrock] & Rupert; Bee Pastures; Oak-wood Grove; 1 Roasted Slowly; Misty Mountain Goblins; Banks of the Anduin; Wolf Rider; Goblin Sniper; Wargs; Despair; The Brown Lands; The East Bight
Setup: Unique:1 & Trait:Troll; 4 Sacked!
Staging Setup: The Carrock
```

**Standalone Scripts**

- `copy_output.py`: Script to copy all set outputs to a destination folder.  For example:
  `python copy_output.py "c:\\Output\\" "Custom Set" "French"`
- `make_unique_png.py`: Script to make unique PNG files for MakePlayingCards.  For example:
  `python make_unique_png.py "c:\\CustomPNG\\"`
- `replace_cmyk_card_backs.py`: Script to replace card backs in existing image archives.  It expects `replace_cmyk_card_backs.txt`
  with a list of direct Mediafire URLs or local file paths to `MBPrint` 7z archives.
- `card_stat.py`: Collect various data from Hall of Beorn and RingsDB and put outputs into `Output/Scripts` folder.

**GIMP Plugins**

You may use GIMP plugins separately.  See the description of each of them in `GIMP/scripts.py`.

Setup:

1. Install GIMP (https://www.gimp.org/downloads/).
2. Open GIMP, go to `Edit` -> `Preferences` -> `Folders` -> `Plug-ins`, add `GIMP` folder
from this repo, click `OK`, and then restart GIMP.

Usage:

For a single image:

1. Open the image file in GIMP
2. Filters -> Script Name
3. Specify Output folder

For a folder:

1. Open any image file in GIMP
2. Filters -> Script Name (with "Folder" at the end)
3. Specify Input folder and Output folder

From CLI:

`gimp-console-2.10 -i -b "(python-<lowercase script name with dashes>-folder 1 \"<path to input folder>\" \"path to output folder\")" -b "(gimp-quit 0)"`

For example:

`gimp-console-2.10 -i -b "(python-prepare-makeplayingcards-folder 1 \"Input\" \"Output\")" -b "(gimp-quit 0)"`

Please note that the name of GIMP console executable on your environment may be slightly different.
