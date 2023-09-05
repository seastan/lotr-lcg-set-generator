# pylint: disable=C0209
""" Script to copy all set outputs to a destination folder.
"""
import os
import re
import shutil
import sys

LANGUAGES = {'English', 'French', 'German', 'Italian', 'Polish', 'Portuguese',
             'Spanish'}
ENGLISH_SUBFOLDERS = [
    'DB',
    'DragnCards',
    'DragnCardsHQ',
    'GenericPNG',
    'GenericPNGPDF',
    'HallOfBeorn',
    'HallOfBeornImages',
    'MakePlayingCards',
    'MBPrint',
    'MBPrintPDF',
    'OCTGN',
    'OCTGNDecks',
    'OCTGNImages',
    'PDF',
    'PreviewImages',
    'RingsDB',
    'RingsDBImages',
    'RulesPDF',
    'TTS'
]
TRANSLATION_SUBFOLDERS = [
    'DB',
    'GenericPNG',
    'GenericPNGPDF',
    'HallOfBeorn',
    'HallOfBeornImages',
    'MakePlayingCards',
    'MBPrint',
    'MBPrintPDF',
    'OCTGNImages',
    'PDF',
    'PreviewImages',
    'RulesPDF'
]
FRENCH_SUBFOLDERS = sorted(TRANSLATION_SUBFOLDERS +
                           ['FrenchDB', 'FrenchDBImages'])
SPANISH_SUBFOLDERS = sorted(TRANSLATION_SUBFOLDERS +
                            ['SpanishDB', 'SpanishDBImages'])
OUTPUT_PATH = 'Output'


def main():  # pylint: disable=R0912
    """ Main function.
    """
    if len(sys.argv) < 3:
        print('Not enough arguments:\n'
              '    python copy_output.py <path to destination folder>'
              ' <set name> [<language>]')
        sys.exit(1)

    destination_folder = sys.argv[1]
    set_name = sys.argv[2]
    if len(sys.argv) > 3:
        language = sys.argv[3]
        if language not in LANGUAGES:
            print('Unknown language: {}'.format(language))
            sys.exit(1)
    else:
        language = 'English'

    if not os.path.exists(destination_folder):
        os.mkdir(destination_folder)

    if language == 'English':
        subfolders = ENGLISH_SUBFOLDERS
    elif language == 'French':
        subfolders = FRENCH_SUBFOLDERS
    elif language == 'Spanish':
        subfolders = SPANISH_SUBFOLDERS
    else:
        subfolders = TRANSLATION_SUBFOLDERS

    for subfolder in subfolders:
        path = os.path.join(OUTPUT_PATH,
                            subfolder,
                            '{}.{}'.format(set_name, language))
        if not os.path.exists(path) and language == 'English':
            path = os.path.join(OUTPUT_PATH, subfolder, set_name)

        if not os.path.exists(path):
            print("Folder {} doesn't exist".format(path))
            continue

        destination_subfolder = os.path.join(destination_folder, subfolder)
        if not os.path.exists(destination_subfolder):
            os.mkdir(destination_subfolder)

        destination_path = os.path.join(destination_subfolder,
                                        os.path.split(path)[-1])
        if os.path.exists(destination_path):
            print('Destination folder {} already exists, skipping'
                  .format(destination_path))
            continue

        shutil.copytree(path, destination_path)

        if subfolder == 'DragnCards':
            for _, _, filenames in os.walk(destination_path):
                for filename in filenames:
                    if (filename.endswith('json.release') or
                            filename.endswith('tsv.release')):
                        shutil.move(
                            os.path.join(destination_path, filename),
                            os.path.join(destination_path,
                                         re.sub(r'\.release$', '', filename)))

                break
        elif subfolder == 'OCTGNDecks':
            for _, _, filenames in os.walk(destination_path):
                for filename in filenames:
                    if filename.startswith('Player-'):
                        os.remove(os.path.join(destination_path, filename))

                break

    print('Done')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
