""" Script to make unique PNG files for MakePlayingCards.
"""
import os
import sys

from lotr import _insert_png_text


def make_unique_png(input_path):
    """ Make unique PNG files for MakePlayingCards.
    """
    for root, _, filenames in os.walk(input_path):
        for filename in filenames:
            if filename.endswith('.png'):
                _insert_png_text(os.path.join(root, filename),
                                 os.path.join(root, filename))


def main():
    """ Main function.
    """
    if len(sys.argv) > 1:
        make_unique_png(sys.argv[1])
    else:
        print('Specify input folder')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
