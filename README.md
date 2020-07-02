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

7. Make sure that macros are enabled in Microsoft Excel.

8. Go to the repo folder.  Either install Anaconda and use it to open a JupyterHub or use VirtualEnv:

  - Install Python 3.7 (or other Python 3 version), Pip and VirtualEnv.
  - `virtualenv env --python=python3.7`
  - `.\env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac)
  - `pip install jupyter pyyaml requests xlwings`
  - `jupyter notebook`

9. Edit `configuration.yaml`:

  - Set `sheet_gdid` (Google Drive ID of the cards spreadsheet).
  - If needed, update `sheet_type` (either `xlsm` or `xlsx`).
  - Set `artwork_path` (local path to the folder with the cropped artwork).

10. Open `setGenerator.ipynb` and follow further instructions.


**GIMP Plugins**

`prepare_makeplayingcards.py`: two plugins to prepare images for MakePlayingCards printing (one for a single image,
another for a folder).  At the moment they make 3 things:

1. rotate landscape images (if image name ends with `-Back-Face` or `-2` then clockwise, otherwise counter-clockwise);
2. crop bleed margins to satisfy MakePlayingCards requirements;
3. export to PNG with the maximum compression level (still lossless, just saves some space).

They support images in 300, 600 and 800 dpi images (original resolution is preserved).

Installation:

1. Open GIMP
2. Edit -> Preferences -> Folders -> Plug-ins
3. Add `gimp` folder from this repo
4. Restart GIMP

Usage:

For a single image:

1. Open image file in GIMP
2. Filters -> Prepare MakePlayingCards
3. Specify Output folder

For a folder:

1. Open GIMP
2. Filters -> Prepare MakePlayingCards Folder
3. Specify Input folder and Output folder

or from CLI:

`gimp-console-2.10 -i -b "(python-prepare-makeplayingcards-folder 1 \"Input\" \"Output\")"`

GIMP executable on your environment may be slightly different.
