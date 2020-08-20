**Setup**

1. Clone this repo to a local folder.

2. Add the folder with the cropped artwork to your own Google Drive to be able to sync it locally.
This feature is currently hidden on the Google Drive UI, but may still be accessed by a shortcut
(see https://support.google.com/drive/thread/35817359?hl=en).  If this feature is removed
completely, you will need to download updates to that folder manually.

3. Install Backup and Sync from Google (if it's not installed yet) and make sure that the folder
with the cropped artwork is being synced.

4. Install the latest available version of Strange Eons (https://strangeeons.cgjennings.ca/download.html)
and the `The Lord of the Rings LCG` plugin.  Then, install `The Lord of the Rings LCG, HD` plugin
as well.

5. Go to plugins folder (`Strange Eons` -> `Toolbox` -> `Manage Plug-ins` -> `Open Plug-in Folder`),
close Strange Eons and replace `TheLordOfTheRingsLCG.seext` with the custom version from this repo.

6. Install GIMP (https://www.gimp.org/downloads/).

7. Open GIMP, go to `Edit` -> `Preferences` -> `Folders` -> `Plug-ins`, add `gimp` folder
from this repo, click `OK` and then close GIMP.

8. Make sure that macros are enabled in Microsoft Excel.

9. Go to the repo folder and follow these steps:

  - Install Python 3.7 (or other Python 3 version), Pip and VirtualEnv.
  - `virtualenv env --python=python3.7`
  - `.\env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac)
  - `pip install jupyter py7zr pylint pyyaml reportlab requests xlwings`

10. Copy `configuration.default.yaml` to `configuration.yaml` and set the following values:

  - `sheet_gdid`: Google Drive ID of the cards spreadsheet
  - `sheet_type`: spreadsheet type, either `xlsm` (default) or `xlsx`
  - `artwork_path`: local path to the folder with the cropped artwork (don't use for that any existing folder in this repo)
  - `gimp_console_path`: path to GIMP console executable
  - `from_scratch`: whether to generate all cards from scratch (`true`) or to update only the cards, changed since the previous script run (`false`)
  - `set_ids`: list of set IDs to work on
  - `languages`: list of languages
  - `outputs`: list of outputs

**Usage**

To run the workflow, go to the repo folder and follow these steps:

- `.\env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac)
- `python run_before_se.py`
- Open `setGenerator.seproject` in Strange Eons and run `Script/makeCards` script by double clicking it.
  Once completed, close Strange Eons (wait until it finished packing the project).
- `python run_after_se.py`

For debugging purposes you can also run these steps using the Jupyter notebook:

- `.\env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac)
- `jupyter notebook`
- Open `setGenerator.ipynb` in the browser.

Now there should be the following outputs:

- `Output/DB/<set name>/`: 300 dpi JPG images for general purposes.
- `Output/MakePlayingCards/<set name>`: `zip` and `7z` archives of 800 dpi PNG images to be printed on MakePlayingCards.com.
- `Output/OCTGN/<octgnid>/:` `set.xml` and `o8c` image pack (300 dpi JPG) for OCTGN.  Add the latter using the "Add Image Packs" button from within OCTGN.
- `Output/PDF/<set name>/`: PDF files in `A4` and `letter` format for home printing.

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