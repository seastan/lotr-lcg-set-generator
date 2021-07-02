**Setup**

Please note that to generate final image outputs, you must run this workflow on a Windows platform,
because each platform renders the fonts differently.

1. Clone this repo to a local folder (you can click `Code` and then `Download ZIP`).

2. Make sure there is a spreadsheet on Google Sheets (most likely, it already exists).

    If it doesn't exist yet (that means you are starting a new project from scratch),
    upload `Spreadsheet/spreadsheet.xlsx` from this repo, click `Save as Google Sheets`,
    click `Share` and `Change to anyone with the link`.  Click `Script editor` and upload the scripts
    from `Spreadsheet/Code.gs`.  After that, re-run `=SHEETS()` function from `A1` cell of the first `-` tab.
    Add all the sets and cards data.

3. Add the folder with the artwork to your Google Drive to be able to sync it locally.
This feature is currently hidden on Google Drive UI, but may still be accessed by a shortcut
(see https://support.google.com/drive/thread/35817359?hl=en).  If this feature is removed
completely, you will need to download updates to that folder manually.

    If it doesn't exist yet (that means you are starting a new project from scratch), create this folder first.
    It should have the following structure:

    ```
    <set ID>/
    <set ID>/<card ID>_<"A" or "B" or "Top" or "Bottom">_<card name and artist, format is not strict>.<"jpg" or "png">
    <set ID>/custom/
    <set ID>/custom/<custom image>
    <set ID>/processed/
    <set ID>/processed/<card ID>_<"A" or "B" or "Top" or "Bottom">_<card name and artist, format is not strict>.<"jpg" or "png">
    custom/
    custom/<custom image>
    icons/
    icons/<icon image>
    ```

    For example:

    ```
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/53dcedb3-3640-4655-a150-9d0dd534a126_A_Reclaim_the_Beacon_Artist_Jan_Pospisil.jpg
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/53dcedb3-3640-4655-a150-9d0dd534a126_B_Defend_the_Beacon_Artist_Skvor.jpg
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/9a677840-6c2d-4603-b2bd-c39464663913_A_Squire_of_the_Mark_Artist_Ekaterina_Burmak.png
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/custom/
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/custom/Encounter-Icons-Ambush-at-Erelas.png
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/processed/
    8a3273ca-1ccd-4e07-913b-766fcc49fe6f/processed/53dcedb3-3640-4655-a150-9d0dd534a126_A_Reclaim_the_Beacon_Artist_Jan_Pospisil.jpg
    custom/
    custom/Do-Not-Read-the-Following.png
    icons/
    icons/ALeP---Children-of-Eorl.png
    icons/Ambush-at-Erelas.png
    ```

    Please note that the files in the `processed` subfolder take precedence over the files in the root folder.

4. Install Backup and Sync from Google (if it's not installed yet) and make sure that the folder
with the artwork is being synced.

    If you plan to automatically upload images to Google Drive (see the configuration below),
    go to `Preferences` -> `Settings` and uncheck `Show warning when you remove items from a shared folder`.

5. Install Strange Eons and the custom plugin, see https://github.com/seastan/lotr-lcg-se-plugin for details.

6. Install the latest GIMP version from https://www.gimp.org/downloads/.

7. Open GIMP, go to `Edit` -> `Preferences` -> `Folders` -> `Plug-ins`, add `GIMP` folder
from this repo, click `OK` and then close GIMP.

8. Install ImageMagick 7.0.10-28 (download Windows version from https://drive.google.com/file/d/1tBFGjE9OakbQNjY-Nqpxky14XVFdGL_G/view?usp=sharing,
for other platforms look at https://download.imagemagick.org/ImageMagick/download/releases/).

9. Download `USWebCoatedSWOP.icc` from
https://github.com/cjw-network/cjwpublish1411/blob/master/vendor/imagine/imagine/lib/Imagine/resources/Adobe/CMYK/USWebCoatedSWOP.icc
into the root folder of this repo.

10. Install AutoHotkey from https://autohotkey.com/download/.

11. Install the latest Python 3 version from https://www.python.org/downloads/.  The minimum supported version is 3.7.
Optionally, install VirtualEnv (see https://help.dreamhost.com/hc/en-us/articles/115000695551-Installing-and-using-virtualenv-with-Python-3
for details).

12. Go to the root folder of this repo and follow these steps:

  - [skip this step, if you don't use VirtualEnv] `virtualenv env --python=python3.9` (replace `3.9` with your actual Python version)
  - [skip this step, if you don't use VirtualEnv] `env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac/Linux)
  - `pip install -r requirements.txt` (if you don't plan to generate images, you may run `pip install -r requirements_cron.txt` instead to skip unneeded dependencies)

    If for debugging purposes you plan to use Jupyter notebook, additionally run:

  - `pip install jupyter`

13. Copy `configuration.default.yaml` to `configuration.yaml` and set the following values:

  - `sheet_gdid`: Google Sheets ID of the cards spreadsheet
  - `artwork_path`: local path to the artwork folder (don't use for that any existing folder in this repo)
  - `gimp_console_path`: path to GIMP console executable
  - `magick_path`: path to ImageMagick executable
  - `dragncards_id_rsa_path`: path to id_rsa key to upload files to DragnCards
  - `remote_logs_path`: path to remote logs folder (may be empty)
  - `octgn_set_xml_destination_path`: path to OCTGN `set.xml` destination folder (may be empty)
  - `octgn_set_xml_scratch_destination_path`: path to OCTGN `set.xml` scratch destination folder (may be empty)
  - `octgn_o8d_destination_path`: path to OCTGN `.o8d` destination folder (may be empty)
  - `octgn_o8d_scratch_destination_path`: path to OCTGN `.o8d` scratch destination folder (may be empty)
  - `octgn_image_destination_path`: path to OCTGN image destination folder (may be empty)
  - `db_destination_path`: path to DB destination folder (may be empty)
  - `tts_destination_path`: path to TTS destination folder (may be empty)
  - `dragncards_remote_image_path`: remote DragnCards path to image folder
  - `dragncards_remote_json_path`: remote DragnCards path to JSON folder
  - `dragncards_remote_deck_path`: remote DragnCards path to .o8d folder
  - `reprocess_all`: whether to reprocess all cards (`true`) or update only the cards, changed since the previous script run (`false`)
  - `reprocess_all_on_error`: whether to reprocess all cards even when reprocess_all=false if the previous script run didn't succeed (true or false)
  - `selected_only`: process only "selected" rows (true or false)
  - `exit_if_no_spreadsheet_changes`: stop processing if there are no spreadsheet changes (true or false)
  - `parallelism`: number of parallel processes to use (`default` means `cpu_count() - 1`, but not more than 4)
  - `set_ids`: list of set IDs to work on (you can use `all` and `all_scratch` aliases to select all non-scratch and all scratch sets sutomatically)
  - `ignore_set_ids`: list of set IDs to ignore
  - `set_ids_octgn_image_destination`: list of set IDs to copy to OCTGN image destination
  - `octgn_set_xml`: creating `set.xml` files for OCTGN (true or false)
  - `octgn_o8d`: creating `.o8d` files for OCTGN and DragnCards (true or false)
  - `ringsdb_csv`: creating CSV files for RingsDB (true or false)
  - `dragncards_json`: creating JSON files for DragnCards (true or false)
  - `hallofbeorn_json`: creating JSON files for Hall of Beorn (true or false)
  - `frenchdb_csv`: creating CSV files for the French database sda.cgbuilder.fr (true or false)
  - `spanishdb_csv`: creating CSV files for the Spanish database susurrosdelbosqueviejo.com (true or false)
  - `upload_dragncards`: uploading outputs to DragnCards (true or false)
  - `dragncards_hostname`: DragnCards hostname (username@hostname)
  - `update_ringsdb`: updating test.ringsdb.com (true or false)
  - `ringsdb_url`: test.ringsdb.com URL
  - `ringsdb_sessionid`: test.ringsdb.com session ID
  - `outputs`: list of image outputs for each language (if you added or uncommented new outputs, you also need to set `reprocess_all` to `true`)

Also, see `configuration.release.yaml` for another configuration example.

**Usage**

To run the workflow, go to the root folder of this repo and follow these steps:

- [skip this step, if you don't use VirtualEnv] `env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac/Linux).
- Make sure that Strange Eons is closed.
- `python run_before_se.py`.
- Pay attention to possible errors in the script output.
- Open `setGenerator.seproject`and run `makeCards` script by double clicking it.
  Once completed, close Strange Eons and wait until it finished packing the project.
- `python run_after_se.py`.
- Pay attention to possible errors in the script output.

For debugging purposes you can also run the steps above using the Jupyter notebook (it doesn't use parallelism):

- [skip this step, if you don't use VirtualEnv] `env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac/Linux)
- `jupyter notebook`
- Open `setGenerator.ipynb` in the browser.

**Automatic Pipeline**

To run the workflow as one script, run:

- `run_all.bat`

Please note, this script is for the Windows platform only.  It uses AutoHotkey to emulate Strange Eons UI commands
and is not 100% reliable (it may stuck on the Strange Eons step).  To minimize the risks:

- Don't leave Strange Eons open.
- Make sure the Strange Eons window was maximized when you closed it.
- Make sure the screen is not locked (and doesn't lock automatically).
- If the script started, don't touch the keyboard or mouse.

If you need to perform some additional actions before and/or after the script starts (like unlocking your PC
or restarting Backup and Sync from Google), you may create two additional batch scripts with your custom code:

- `run_setup.bat`
- `run_cleanup.bat`

They will be called inside `run_all.bat` automatically.  See `run_setup.bat.example` for an example.

Also, see `configuration.nightly.yaml` for a configuration example.

If you want to set up a Windows cron job, do the following:

- Run `Task Scheduler`.
- Click `Create Task`.
- Set `Name`.
- Click `Triggers` -> `New`.
- Set up a schedule and click `OK`.
- Click `Actions` -> `New`.
- Click `Browse...`, choose `run_all.bat` and click `OK`.
- Click `OK`.

**Cron Job Pipeline**

See `configuration.cron.yaml` for a configuration example.

T.B.D.

**Outputs**

The scripts will generate the following outputs:

- `Output/DB/<set name>.<language>/`: 300 dpi PNG images for general purposes (including TTS).
- `Output/DragnCards/<set name>/<set name>.json`: an output file for DragnCards.
- `Output/DriveThruCards/<set name>.<language>/`: a `7z` archive of 300 dpi CMYK JPG images to be printed on DriveThruCards.com.
- `Output/FrenchDB/<set name>/`: CSV files for French database sda.cgbuilder.fr.
- `Output/FrenchDBImages/<set name>.<language>/`: 300 dpi PNG images for French database (the same as `Output/DB`, but differently named).
- `Output/GenericPNG/<set name>.<language>/`: a `7z` archive of generic 800 dpi PNG images.
- `Output/GenericPNGPDF/<set name>.<language>/`: `7z` archives of PDF files in `A4` and `letter` format (800 dpi PNG).
- `Output/HallOfBeorn/<set name>/<set name>.json`: an output file for Hall of Beorn.
- `Output/MakePlayingCards/<set name>.<language>/`: a `7z` archive of 800 dpi PNG images to be printed on MakePlayingCards.com.
- `Output/MBPrint/<set name>.<language>/`: a `7z` archive of 800 dpi CMYK JPG images to be printed on MBPrint.pl.
- `Output/MBPrintPDF/<set name>.<language>/`: a `7z` archive of a PDF file to be printed on MBPrint.pl (800 dpi CMYK JPG).
- `Output/OCTGN/<set name>/<octgn id>/set.xml`: an output file for OCTGN.
- `Output/OCTGNDecks/<set name>/<deck name>.o8d`: quest decks for OCTGN and DragnCards.
- `Output/OCTGNImages/<set name>.<language>/<set name>.<language>.o8c`: image packs for OCTGN and DragnCards (600x429 JPG).
- `Output/PDF/<set name>.<language>/`: PDF files in `A4` and `letter` format for home printing (300 dpi PNG).
- `Output/PreviewImages/<set name>.<language>/`: 600x429 JPG images for preview purposes.
- `Output/RingsDB/<set name>/<set name>.csv`: an output file for RIngsDB.
- `Output/RingsDBImages/<set name>/`: 300 dpi PNG images for RingsDB (the same as `Output/DB`, but player cards only and differently named).
- `Output/RulesPDF/<set name>.<language>/Rules.<set name>.<language>.pdf`: a PDF file with all Rules pages (300 dpi PNG).
- `Output/SpanishDB/<set name>/`: CSV files for Spanish database susurrosdelbosqueviejo.com.
- `Output/SpanishDBImages/<set name>.<language>/`: 300 dpi PNG images for Spanish database (the same as `Output/DB`, but differently named).
- `Output/TTS/<set name>.<language>/`: 300 dpi JPG image sheets for TTS.

Please note that `Output/DB`, `Output/PreviewImages`, `Output/RingsDBImages` (for English language only),
`Output/FrenchDBImages` (for French language only) and `Output/SpanishDBImages` (for Spanish language only)
are generated when `db` output is enabled in the configuration.

When `tts` output is enabled in the configuration, `octgn_o8d` and `db` outputs become enabled automatically.

Additionally, if you specified OCTGN destination paths, OCTGN outputs will be copied there.

**Supported Tags**

- `[center]` ... `[/center]`: center alignment
- `[right]` ... `[/right]`: right alignment
- `[b]` ... `[/b]`: bold text
- `[i]` ... `[/i]`: italic text
- `[bi]` ... `[/bi]`: bold + italic text
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
- `[inline]`: put it at the end of the `Keywords` field, to place the keywords on the same line as the first line of text
- `[name]`: actual card name
- `[lsb]`: [
- `[rsb]`: ]
- `[lquot]`: unmatched left quote
- `[rquot]`: unmatched right quote
- `[lfquot]`: unmatched French left quote
- `[rrquot]`: unmatched French right quote
- `[quot]`: "
- `[apos]`: '
- `[hyphen]`: -
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
- `Enemy`
- `Encounter Side Quest` (alias: `Side Quest`)
- `Event`
- `Hero`
- `Location`
- `Nightmare`
- `Objective`
- `Objective Ally`
- `Objective Hero`
- `Objective Location`
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
- `Burden`
- `Nightmare`
- `Upgraded`
- `Back` (`Rules` only)
- `Setup` (`Campaign` only)
- `Blue` (`Presentation` only)
- `Green` (`Presentation` only)
- `Purple` (`Presentation` only)
- `Red` (`Presentation` only)
- `Brown` (`Presentation` only)
- `Yellow` (`Presentation` only)
- `Nightmare Blue` (`Presentation` only)
- `Nightmare Green` (`Presentation` only)
- `Nightmare Purple` (`Presentation` only)
- `Nightmare Red` (`Presentation` only)
- `Nightmare Brown` (`Presentation` only)
- `Nightmare Yellow` (`Presentation` only)

Please note, that not all card types and spheres are currently supported by Strange Eons.

To choose the promo template for a hero, put "Promo" into `Adventure` column.

**Special Icons**

- `Eye Of Sauron`
- `Sailing`

**Deck Rules**

OCTGN `.o8d` files are generated automatically for each scenario detected on `Quest` and `Nightmare` cards.
By default, the deck includes all cards, which share both the set and encounter set from the
"parent" `Quest` or `Nightmare` card (including encounter sets from `Additional Encounter Sets` column).
All `Quest`, `Nightmare`, and `Campaign` cards are put into `Quest` section, all `Rules`
cards are put into `Setup` section and all encounter cards are put into `Encounter` section.
Filename of the deck is the same as `Adventure` value (`Quest` cards) or `Name` value (`Nightmare` cards)
with all spaces replaced with `-`.  Easy mode version is generated automatically if any card included
in the deck has a different quantity for the normal and easy modes.

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
Prefix: QA1.5-ALeP
```

If you want to set a list of values, separate them by `;`.  For example:

```
Setup: Saruman; Grima; Brandywine Gate
```

Below is a list of all supported rules:

- `Prefix`: A **mandatory** filename prefix.  It must start with:
  `<either "Q" (normal mode) or "N" (nightmare mode)><two capital letters and/or numbers>.<one or two numbers><end of string, space or dash>`.
  For example, `Prefix: Q0B.19-Standalone-ALeP` will result in a filename like `Q0B.19-Standalone-ALeP-The-Scouring-of-the-Shire.o8d`.
- `Sets`: Additional sets to be included.  For example: `Sets: ALeP - Children of Eorl`.
- `Encounter Sets`: Additional encounter sets to be included.  For example:
  `Encounter Sets: Journey in the Dark`.
- `External XML`: Links to external `set.xml` files (if those cards are not in the spreadsheet).
  For example: `External XML: https://raw.githubusercontent.com/seastan/Lord-of-the-Rings/master/o8g/Sets/The%20Road%20Darkens/set.xml`.
- `Remove`: List of filters to select cards that need to be removed from the deck.  For example:
  `Remove: Type:Campaign` (remove any cards with `Campaign` type from the normal deck).
- `Second Quest Deck`, `Special`, `Second Special`, `Setup`, `Staging Setup`, and `Active Setup`:
  List of filters to select cards for that section.  For example: `Setup: Saruman; Grima; Brandywine Gate`.
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
Prefix: Q0B.19-Standalone-ALeP
Remove: Type:Campaign
Special: Trait:Sharkey & Type:Treachery
Setup: Saruman; Grima; Brandywine Gate; Type:Side Quest; 4 One-feather Shirriff
Player: Frodo Baggins

Prefix: Q0C.19-Campaign-ALeP
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
Prefix: N01.5 Nightmare
External XML: https://raw.githubusercontent.com/seastan/Lord-of-the-Rings/master/o8g/Sets/Core%20Set/set.xml; https://raw.githubusercontent.com/seastan/Lord-of-the-Rings/master/o8g/Sets/Conflict%20at%20the%20Carrock/set.xml; https://raw.githubusercontent.com/seastan/Lord-of-the-Rings/master/o8g/Sets/Shadows%20of%20Mirkwood%20-%20Nightmare/set.xml
Sets: Core Set; Conflict at the Carrock; Shadows of Mirkwood - Nightmare
Encounter Sets: Journey Down the Anduin; Wilderlands; Conflict at the Carrock; Conflict at the Carrock - Nightmare
Remove: [Journey Down the Anduin] & Type:Quest; Grimbeorn the Old; [Conflict at the Carrock] & Louis; [Conflict at the Carrock] & Morris; [Conflict at the Carrock] & Stuart; [Conflict at the Carrock] & Rupert; Bee Pastures; Oak-wood Grove; 1 Roasted Slowly; Misty Mountain Goblins; Banks of the Anduin; Wolf Rider; Goblin Sniper; Wargs; Despair; The Brown Lands; The East Bight
Setup: Unique:1 & Trait:Troll; 4 Sacked!
Staging Setup: The Carrock
```

**Standalone Scripts**

- `hallofbeorn_stat.py`: Collect various statistics from Hall of Beorn and put outputs into `Output/Scripts` folder.

**GIMP Plugins**

You may use GIMP plugins separately.  See the description of each of them in `GIMP/scripts.py`.

Setup:

1. Install GIMP (https://www.gimp.org/downloads/).
2. Open GIMP, go to `Edit` -> `Preferences` -> `Folders` -> `Plug-ins`, add `GIMP` folder
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
