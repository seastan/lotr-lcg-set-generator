**Setup**

1. Clone this repo to a local folder.

2. Make sure you already have a cards spreadsheet on Google Sheets.  If you don't, upload
`Spreadsheet/spreadsheet.xlsx` from this repo as a template and fill in all the required data.
You will also need to upload Google Apps scripts from `Spreadsheet/Code.gs`.  After that,
re-run `=SHEETS()` function from `A1` cell of the first `-` tab.

3. Add the folder with the artwork to your Google Drive to be able to sync it locally.
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

5. Install Strange Eons and the custom plugin, see https://github.com/seastan/lotr-lcg-se-plugin for details.

6. Install GIMP (https://www.gimp.org/downloads/).

7. Open GIMP, go to `Edit` -> `Preferences` -> `Folders` -> `Plug-ins`, add `GIMP` folder
from this repo, click `OK` and then close GIMP.

8. Install ImageMagick (https://imagemagick.org/script/download.php).

9. Download `Vafthrudnir` font from https://www.wfonts.com/font/vafthrudnir.  Install it together with `Vafthaurdir`
font from the root folder of this repo.  Additionally, manually copy both `.ttf` files into your system fonts folder
(`C:\Windows\Fonts` in Windows), if they are not there.  Otherwise, Strange Eons won't detect them.

10. Download `USWebCoatedSWOP.icc` from
https://github.com/cjw-network/cjwpublish1411/blob/master/vendor/imagine/imagine/lib/Imagine/resources/Adobe/CMYK/USWebCoatedSWOP.icc
into the root folder of this repo.

11. Install Python 3.8 (or other Python 3 version), Pip and VirtualEnv.

12. Go to the root folder of this repo and follow these steps:

  - `virtualenv env --python=python3.8` (if needed, replace `3.8` with your actual Python version)
  - `.\env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac)
  - `pip install -r requirements.txt`

13. Copy `configuration.default.yaml` to `configuration.yaml` and set the following values:

  - `sheet_gdid`: Google Sheets ID of the cards spreadsheet (leave empty to use a local copy)
  - `artwork_path`: local path to the artwork folder (don't use for that any existing folder in this repo)
  - `gimp_console_path`: path to GIMP console executable
  - `magick_path`: path to ImageMagick executable
  - `octgn_set_xml_destination_path`: path to OCTGN `set.xml` destination folder (may be empty)
  - `octgn_set_xml_scratch_destination_path`: path to OCTGN `set.xml` scratch destination folder (may be empty)
  - `octgn_o8d_destination_path`: path to OCTGN `.o8d` destination folder (may be empty)
  - `octgn_o8d_scratch_destination_path`: path to OCTGN `.o8d` scratch destination folder (may be empty)
  - `reprocess_all`: whether to reprocess all cards (`true`) or update only the cards, changed since the previous script run (`false`)
  - `selected_only`: process only "selected" rows (true or false)
  - `parallelism`: number of parallel processes to use (`default` means `cpu_count() - 1`)
  - `set_ids`: list of set IDs to work on (you can use `all` and `all_scratch` aliases to select all non-scratch and all scratch sets sutomatically)
  - `octgn_set_xml`: creating `set.xml` files for OCTGN (true or false)
  - `octgn_o8d`: creating `.o8d` files for OCTGN (true or false)
  - `ringsdb_csv`: creating CSV files for RingsDB (true or false)
  - `hallofbeorn_json`: creating JSON files for Hall of Beorn (true or false)
  - `outputs`: list of image outputs for each language (if you added or uncommented new outputs, you also need to set `reprocess_all` to `true`)

**Usage**

To run the workflow, go to the root folder of this repo and follow these steps:

- `.\env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac)
- `python run_before_se.py` (or `python run_before_se.py <path to a different configuration yaml>` if you want to pass a different configuration file)
- Open `setGenerator.seproject` in Strange Eons and run `Script/makeCards` script by double clicking it.
  Once completed, close Strange Eons and wait until it finished packing the project.
- `python run_after_se.py` (or `python run_after_se.py <path to a different configuration yaml>` if you want to pass a different configuration file)

For debugging purposes you can also run these steps using the Jupyter notebook (it doesn't use parallelism):

- `.\env\Scripts\activate.bat` (Windows) or `source env/bin/activate` (Mac)
- `jupyter notebook`
- Open `setGenerator.ipynb` in the browser.

The scripts will generate the following outputs:

- `Output/DB/<set name>.<language>/`: 300 dpi PNG images for general purposes.
- `Output/DriveThruCards/<set name>.<language>/`: `zip` and `7z` archives of 300 dpi JPG images to be printed on DriveThruCards.com.
- `Output/GenericPNG/<set name>.<language>/`: `zip` and `7z` archives of generic 800 dpi PNG images.
- `Output/HallOfBeorn/<set name>.json`.
- `Output/MakePlayingCards/<set name>.<language>/`: `zip` and `7z` archives of 800 dpi PNG images to be printed on MakePlayingCards.com.
- `Output/MBPrint/<set name>.<language>/`: `zip` and `7z` archives and a PDF file of 800 dpi JPG images to be printed on MBPrint.pl.
- `Output/OCTGN/<set name>/<octgn id>/set.xml`.
- `Output/OCTGN/<set name>/<set name>.<language>.o8c`: image packs for OCTGN (300 dpi PNG).
- `Output/OCTGNDecks/<set name>/<deck name>.o8d`: quest decks for OCTGN.
- `Output/PDF/<set name>.<language>/`: PDF files in `A4` and `letter` format for home printing (300 dpi PNG).
- `Output/RingsDB/<set name>.csv`.

Additionally, if you specified OCTGN destination paths, OCTGN outputs will be copied there.

**Supported Tags**

- `[center]` ... `[/center]`: center alignment
- `[right]` ... `[/right]`: right alignment
- `[b]` ... `[/b]`: bold text
- `[i]` ... `[/i]`: italic text
- `[bi]` ... `[/bi]`: bold + italic text
- `[u]` ... `[/u]`: underlined text
- `[strike]` ... `[/strike]`: strikethrough text
- `[red]` ... `[/red]`: red text
- `[lotr X]` ... `[/lotr]`: Vafthrundir font + text size X (X may be float)
- `[size X]` ... `[/size]`: text size X (X may be float)
- `[defaultsize X]`: put it at the beginning of a field, to set default text size X (X may be float)
- `[img PATH]`: insert image from PATH (PATH may start either with "custom/" or "icons/")
- `[img PATH Xin]`: insert image from PATH and set its width to X inches
- `[img PATH Xin Yin]`: insert image from PATH and set its width to X inches and its height to Y inches
- `[space]`: horizontal spacing
- `[tab]`: tab symbol
- `[nobr]`: non-breakable space
- `[inline]`: put it at the end of the `Keywords` field, to place the keywords on the same line as the first line of text
- `[name]`: actual card name
- `[lsb]`: [
- `[rsb]`: ]
- `[lquot]`: unmatched “
- `[rquot]`: unmatched ”
- `[quot]`: "
- `[apos]`: '
- `[hyphen]`: -
- `--`: – (en dash)
- `---`: — (em dash)

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
- `Setup` (`Campaign` only)
- `Upgraded` (`Ship Objective` only)
- `Blue` (`Presentation` only)
- `Green` (`Presentation` only)
- `Purple` (`Presentation` only)
- `Red` (`Presentation` only)
- `Brown` (`Presentation` only)
- `Yellow` (`Presentation` only)

Please note, that not all card types and spheres are currently supported by Strange Eons.

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
Prefix: ALeP-Standalone-01
```

If you want to set a list of values, separate them by `;`.  For example:

```
Setup: Saruman; Grima; Brandywine Gate
```

Below is a list of all supported rules:

- `Prefix`: Specify a custom filename prefix.  For example: `Prefix: ALeP-Standalone-01` will result
  in a filename like `ALeP-Standalone-01-The-Scouring-of-the-Shire.o8d`.
- `Sets`: Specify additional sets to be included.  For example: `Sets: ALeP - Children of Eorl`.
- `Encounter Sets`: Specify additional encounter sets to be included.  For example:
  `Encounter Sets: Journey in the Dark`.
- `External XML`: links to external `set.xml` files (if those cards are not in the spreadsheet).
  For example: `External XML: https://raw.githubusercontent.com/seastan/Lord-of-the-Rings/master/o8g/Sets/The%20Road%20Darkens/set.xml`.
- `Remove`: list of filters to select cards that need to be removed from the deck.  For example:
  `Remove: Type:Campaign` (remove any cards with `Campaign` type from the normal deck).
- `Second Quest Deck`, `Special`, `Second Special`, `Setup`, `Staging Setup`, and `Active Setup`:
  list of filters to select cards for that section.  For example: `Setup: Saruman; Grima; Brandywine Gate`.
- `Player`: list of filters to select cards for `Hero`, `Ally`, `Attachment`, `Event`, and `Side Quest`
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
Prefix: ALeP-Standalone-01
Remove: Type:Campaign
Special: Trait:Sharkey & Type:Treachery
Setup: Saruman; Grima; Brandywine Gate; Type:Side Quest; 4 One-feather Shirriff
Player: Frodo Baggins

Prefix: ALeP-Standalone-01-Campaign
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
Prefix: Nightmare-1.5
External XML: https://raw.githubusercontent.com/seastan/Lord-of-the-Rings/master/o8g/Sets/Core%20Set/set.xml; https://raw.githubusercontent.com/seastan/Lord-of-the-Rings/master/o8g/Sets/Conflict%20at%20the%20Carrock/set.xml; https://raw.githubusercontent.com/seastan/Lord-of-the-Rings/master/o8g/Sets/Shadows%20of%20Mirkwood%20-%20Nightmare/set.xml
Sets: Core Set; Conflict at the Carrock; Shadows of Mirkwood - Nightmare
Encounter Sets: Journey Down the Anduin; Wilderlands; Conflict at the Carrock; Conflict at the Carrock - Nightmare
Remove: [Journey Down the Anduin] & Type:Quest; Grimbeorn the Old; [Conflict at the Carrock] & Louis; [Conflict at the Carrock] & Morris; [Conflict at the Carrock] & Stuart; [Conflict at the Carrock] & Rupert; Bee Pastures; Oak-wood Grove; 1 Roasted Slowly; Misty Mountain Goblins; Banks of the Anduin; Wolf Rider; Goblin Sniper; Wargs; Despair; The Brown Lands; The East Bight
Setup: Unique:1 & Trait:Troll; 4 Sacked!
Staging Setup: The Carrock
```

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