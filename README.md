**Setup**

1. Clone this repo to a local folder.

2. Make sure you already have a cards spreadsheet on Google Drive.  If you don't, upload
`spreadsheet.xlsx` from this repo as a template and fill in all the required data.

3. Add the folder with the artwork to your own Google Drive to be able to sync it locally.
This feature is currently hidden on Google Drive UI, but may still be accessed by a shortcut
(see https://support.google.com/drive/thread/35817359?hl=en).  If this feature is removed
completely, you will need to download updates to that folder manually.

    Create this folder if it doesn't exist yet.  It should have the following structure:

    ```
    <set ID>/
    <set ID>/<card ID>_<"A" or "B" or "Top" or "Bottom">_<card name and artist, format is not strict>.<"jpg" or "png">
    <set ID>/custom/
    <set ID>/custom/<custom image>
    <set ID>/processed/
    <set ID>/processed/<card ID>_<"A" or "B" or "Top" or "Bottom">_<card name and artist, format is not strict>.<"jpg" or "png">
    ```

    For example:

    ```
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/53dcedb3-3640-4655-a150-9d0dd534a126_A_Reclaim_the_Beacon_Artist_Jan_Pospisil.jpg
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/53dcedb3-3640-4655-a150-9d0dd534a126_B_Defend_the_Beacon_Artist_Skvor.jpg
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/9a677840-6c2d-4603-b2bd-c39464663913_A_Squire_of_the_Mark_Artist_Ekaterina_Burmak.png
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/custom/
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/custom/rules.png
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/processed/
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/processed/53dcedb3-3640-4655-a150-9d0dd534a126_A_Reclaim_the_Beacon_Artist_Jan_Pospisil.jpg
    ```

    Please note that the files in the `processed` subfolder take precedence over the files in the root folder.

4. Install Backup and Sync from Google (if it's not installed yet) and make sure that the folder
with the artwork is being synced.

5. Install the latest version of Strange Eons (https://strangeeons.cgjennings.ca/download.html),
run it and install `The Lord of the Rings LCG` plugin.

6. If you want to use the old version of plugin, additionally install `The Lord of the Rings LCG, HD`
plugin.  Then, go to plugins folder (`Strange Eons` -> `Toolbox` -> `Manage Plug-ins` -> `Open Plug-in Folder`),
close Strange Eons and replace `TheLordOfTheRingsLCG.seext` with the file from this repo.

   If you want to use the new version of plugin, then download its archive manually (we don't provide a link here).
   Then, go to plugins folder (`Strange Eons` -> `Toolbox` -> `Manage Plug-ins` -> `Open Plug-in Folder`),
   close Strange Eons and delete or move all files, which names start with `TheLordOfTheRingsLCG`.  Instead of them,
   copy all files from the new archive.

7. Install GIMP (https://www.gimp.org/downloads/).

8. Open GIMP, go to `Edit` -> `Preferences` -> `Folders` -> `Plug-ins`, add `gimp` folder
from this repo, click `OK` and then close GIMP.

9. Install ImageMagick (https://imagemagick.org/script/download.php).

10. Download `USWebCoatedSWOP.icc` from
https://github.com/cjw-network/cjwpublish1411/blob/master/vendor/imagine/imagine/lib/Imagine/resources/Adobe/CMYK/USWebCoatedSWOP.icc
into the root folder of this repo.

11. Make sure that macros are enabled in Microsoft Excel.

12. Install Python 3.8 (or other Python 3 version), Pip and VirtualEnv.

13. Go to the repo folder and follow these steps:

  - `virtualenv env --python=python3.8` (replace `3.8` with your actual Python version)
  - `.\env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac)
  - `pip install -r requirements.txt`

14. Copy `configuration.default.yaml` to `configuration.yaml` and set the following values:

  - `sheet_gdid`: Google Drive ID of the cards spreadsheet (leave empty to use a local copy)
  - `artwork_path`: local path to the artwork folder (don't use for that any existing folder in this repo)
  - `gimp_console_path`: path to GIMP console executable
  - `magick_path`: path to ImageMagick executable
  - `octgn_destination_path`: path to OCTGN destination folder (may be empty)
  - `reprocess_all`: whether to reprocess all cards (`true`) or update only the cards, changed since the previous script run (`false`)
  - `selected_only`: process only "selected" rows (true or false)
  - `parallelism`: number of parallel processes to use (`default` means `cpu_count() - 1`)
  - `strange_eons_plugin_version`: version of Strange Eons plugin, either `new` or `old`
  - `set_ids`: list of set IDs to work on (you can use `[all]` and `[all scratch]` aliases to select all non-scratch and all scratch sets sutomatically)
  - `octgn_set_xml`: creating set.xml files for OCTGN (true or false)
  - `ringsdb_csv`: creating CSV files for RingsDB (true or false)
  - `hallofbeorn_json`: creating JSON files for Hall of Beorn (true or false)
  - `outputs`: list of image outputs for each language (if you added or uncommented new outputs, you also need to set `reprocess_all` to `true`)

**Usage**

To run the workflow, go to the repo folder and follow these steps:

- `.\env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac)
- `python run_before_se.py` (or `python run_before_se.py <path to a different configuration yaml>` if you want to pass a different configuration file)
- Open `setGenerator.seproject` in Strange Eons and run `Script/makeCards` script by double clicking it.
  Once completed, close Strange Eons (wait until it finished packing the project).
- `python run_after_se.py` (or `python run_after_se.py <path to a different configuration yaml>` if you want to pass a different configuration file)

For debugging purposes you can also run these steps using the Jupyter notebook (it doesn't use parallelism):

- `.\env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac)
- `jupyter notebook`
- Open `setGenerator.ipynb` in the browser.

Now there should be the following outputs:

- `Output/DB/<set name>.<language>/`: 300 dpi PNG images for general purposes.
- `Output/DriveThruCards/<set name>.<language>/`: `zip` and `7z` archives of 300 dpi JPG images to be printed on DriveThruCards.com.
- `Output/HallOfBeorn/<set name>.json`.
- `Output/MakePlayingCards/<set name>.<language>/`: `zip` and `7z` archives of 800 dpi PNG images to be printed on MakePlayingCards.com.
- `Output/OCTGN/<set name>/<octgn id>/set.xml`.
- `Output/OCTGN/<set name>/<set name>.<language>.o8c`: image packs for OCTGN (300 dpi PNG).
- `Output/PDF/<set name>.<language>/`: PDF files in `A4` and `letter` format for home printing.
- `Output/RingsDB/<set name>.csv`.

Additionally, if you specified `octgn_destination_path`, `set.xml` files for OCTGN will be copied there.

**GIMP Plugins**

You may use GIMP plugins separately.  See the description of each of them in `gimp/scripts.py`.

Setup:

1. Install GIMP (https://www.gimp.org/downloads/).
2. Open GIMP, go to `Edit` -> `Preferences` -> `Folders` -> `Plug-ins`, add `gimp` folder
from this repo, click `OK` and then restart GIMP.

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