1. Clone the repo
2. Install Anaconda and use it to open a JupyterHub.  As another option, you can use VirtualEnv:

   - `virtualenv env --python=python3.7`
   - `.\env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac)
   - `pip install jupyter requests xlwings`
   - `jupyter notebook`

3. Open the setGenerator.ipynb notebook
4. Run through the notebook to make the set

`BulkExport.seplugin`: an updated version of Bulk Export plugin with 800 dpi support (450 dpi has been removed).

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
