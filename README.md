**Setup**

1. Clone this repo to a local folder.

2. Add the folder with the cropped artwork to your own Google Drive to be able to sync it locally.
This feature is currently hidden on the Google Drive UI, but may still be accessed by a shortcut
(see https://support.google.com/drive/thread/35817359?hl=en).  If this feature is removed
completely, you will need to download updates to that folder manually.

  The folder should have the following structure:

  ```
  <set ID>/
  <set ID>/<card ID>_<"A" or "B">_<card name and artist, format is not strict>.<"jpg" or "png">
  <set ID>/processed/
  <set ID>/processed/<card ID>_<"A" or "B">_<card name and artist, format is not strict>.<"jpg" or "png">
  ```

  For example:

  ```
  8a3273ca-1ccd-4e07-913b-766fcc49fe6f/
  8a3273ca-1ccd-4e07-913b-766fcc49fe6f/53dcedb3-3640-4655-a150-9d0dd534a126_A_Reclaim_the_Beacon_Artist_Jan_Pospisil.jpg
  8a3273ca-1ccd-4e07-913b-766fcc49fe6f/53dcedb3-3640-4655-a150-9d0dd534a126_B_Defend_the_Beacon_Artist_Skvor.jpg
  8a3273ca-1ccd-4e07-913b-766fcc49fe6f/9a677840-6c2d-4603-b2bd-c39464663913_A_Squire_of_the_Mark_Artist_Ekaterina_Burmak.png
  8a3273ca-1ccd-4e07-913b-766fcc49fe6f/processed/
  8a3273ca-1ccd-4e07-913b-766fcc49fe6f/processed/53dcedb3-3640-4655-a150-9d0dd534a126_A_Reclaim_the_Beacon_Artist_Jan_Pospisil.jpg
  ```

  Please note that the files in the `processed` folder take precedence over the files in the root folder.

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

8. Install ImageMagick (https://imagemagick.org/script/download.php).

9. Download `USWebCoatedSWOP.icc` from
https://github.com/cjw-network/cjwpublish1411/blob/master/vendor/imagine/imagine/lib/Imagine/resources/Adobe/CMYK/USWebCoatedSWOP.icc
into the root folder of this repo.

10. Make sure that macros are enabled in Microsoft Excel.

11. Go to the repo folder and follow these steps:

  - Install Python 3.7 (or other Python 3 version), Pip and VirtualEnv.
  - `virtualenv env --python=python3.7`
  - `.\env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac)
  - `pip install jupyter py7zr pylint pypng pyyaml reportlab requests xlwings`

12. Copy `configuration.default.yaml` to `configuration.yaml` and set the following values:

  - `sheet_gdid`: Google Drive ID of the cards spreadsheet
  - `sheet_type`: spreadsheet type, either `xlsm` (default) or `xlsx`
  - `artwork_path`: local path to the folder with the cropped artwork (don't use for that any existing folder in this repo)
  - `gimp_console_path`: path to GIMP console executable
  - `magick_path`: path to ImageMagick executable
  - `octgn_destination_path`: path to OCTGN destination folder (may be empty)
  - `from_scratch`: whether to generate all cards from scratch (`true`) or to process only the cards, changed since the previous script run (`false`)
  - `parallelism`: number of parallel processes to use (`default` means `cpu_count() - 1`)
  - `set_ids`: list of set IDs to work on
  - `languages`: list of languages
  - `outputs`: list of outputs (if you added new outputs, you also need to set `from_scratch` to `true`)

**Usage**

To run the workflow, go to the repo folder and follow these steps:

- `.\env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac)
- `python run_before_se.py`
- Open `setGenerator.seproject` in Strange Eons and run `Script/makeCards` script by double clicking it.
  Once completed, close Strange Eons (wait until it finished packing the project).
- `python run_after_se.py`

For debugging purposes you can also run these steps using the Jupyter notebook (it doesn't use parallelism):

- `.\env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac)
- `jupyter notebook`
- Open `setGenerator.ipynb` in the browser.

Now there should be the following outputs:

- `Output/OCTGN/<set name>/`: `<octgn id>/set.xml` and `<set name>.<language>.o8c` image packs for OCTGN (300 dpi JPG).
- `Output/DB/<set name>.<language>/`: 300 dpi JPG images for general purposes.
- `Output/PDF/<set name>.<language>/`: PDF files in `A4` and `letter` format for home printing.
- `Output/DriveThruCards/<set name>.<language>/`: `zip` and `7z` archives of 300 dpi PNG images to be printed on DriveThruCards.com.
- `Output/MakePlayingCards/<set name>.<language>/`: `zip` and `7z` archives of 800 dpi PNG images to be printed on MakePlayingCards.com.

Additionally, if you specified `octgn_destination_path`, OCTGN outputs will be copied there.

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