**Setup**

1. Clone this repo to a local folder.

2. Add the folder with the cropped artwork to your own Google Drive to be able to sync it locally.
This feature is currently hidden on the Google Drive UI, but may still be accessed by a shortcut
(see https://support.google.com/drive/thread/35817359?hl=en).  If this feature is removed
completely, you will need to download updates to that folder manually.

3. Install Backup and Sync from Google (if it's not installed yet) and make sure that the folder
with the cropped artwork is being synced.

4. Install the latest available version of Strange Eons (https://strangeeons.cgjennings.ca/download.html)
and the `The Lord of the Rings LCG` plugin.  Additionally, install `Bulk Export`, `Developer Tools`
and `The Lord of the Rings LCG, HD` plugins.

5. Go to plugins folder (`Strange Eons` -> `Toolbox` -> `Manage Plug-ins` -> `Open Plug-in Folder`),
close Strange Eons and replace `TheLordOfTheRingsLCG.seext` and `BulkExport.seplugin` with the custom
versions from this repo.

6. Install GIMP (https://www.gimp.org/downloads/).

7. Open GIMP, go to `Edit` -> `Preferences` -> `Folders` -> `Plug-ins`, add `gimp` folder
from this repo, click `OK` and then close GIMP.

8. Make sure that macros are enabled in Microsoft Excel.

9. Go to the repo folder.  Either use Anaconda to install Python dependenices and open a JupyterHub
or just use VirtualEnv:

  - Install Python 3.7 (or other Python 3 version), Pip and VirtualEnv.
  - `virtualenv env --python=python3.7`
  - `.\env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac)
  - `pip install jupyter pylint pyyaml reportlab requests xlwings`
  - `jupyter notebook`

10. Edit `configuration.yaml`:

  - Set `sheet_gdid` (Google Drive ID of the cards spreadsheet).
  - If needed, update `sheet_type` (either `xlsm` or `xlsx`).
  - Set `artwork_path` (local path to the folder with the cropped artwork, don't use any existing folder in this repo).
  - Set `gimp_console_path` (path to GIMP console executable).

11. Open `setGenerator.ipynb` and follow further instructions.


**GIMP Plugins**

You may use GIMP plugins separately.  See description of each of them in `gimp/scripts.py`.

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