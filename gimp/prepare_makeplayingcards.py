#!/usr/bin/env python
""" Custom GIMP plugin(s).
"""
import os
from gimpfu import (gimp, pdb, register, main, PF_IMAGE, PF_DRAWABLE,
                    PF_DIRNAME, ROTATE_90, ROTATE_270)

def prepare_makeplayingcards(img, drawable, output_folder):
    """ Prepare an image for MakePlayingCards printing.
    """
    gimp.progress_init('Prepare an image for MakePlayingCards printing...')
    pdb.gimp_undo_push_group_start(img)

    back_side = False
    rotate = False
    clip_size = 0

    try:
        file_name = pdb.gimp_image_get_filename(img)
        file_name = os.path.split(file_name)[-1]
        file_name = '.'.join(file_name.split('.')[:-1])
        if file_name.endswith('-Back-Face') or file_name.endswith('-2'):
            back_side = True

        file_name = file_name + '.png'
    except Exception:  # pylint: disable=W0703
        pdb.gimp_undo_push_group_end(img)
        return

    if drawable.width == 826 and drawable.height == 1126:
        clip_size = 2
    elif drawable.width == 1126 and drawable.height == 826:
        rotate = True
        clip_size = 2
    elif drawable.width == 1650 and drawable.height == 2250:
        clip_size = 3
    elif drawable.width == 2250 and drawable.height == 1650:
        rotate = True
        clip_size = 3
    elif drawable.width == 2200 and drawable.height == 3000:
        clip_size = 4
    elif drawable.width == 3000 and drawable.height == 2200:
        rotate = True
        clip_size = 4

    if rotate:
        if back_side:
            pdb.gimp_item_transform_rotate_simple(drawable, ROTATE_90, False,
                                                  drawable.height / 2,
                                                  drawable.height / 2)
        else:
            pdb.gimp_item_transform_rotate_simple(drawable, ROTATE_270, False,
                                                  drawable.width / 2,
                                                  drawable.width / 2)

    if clip_size:
        new_width = drawable.width - 2 * clip_size
        new_height = drawable.height - 2 * clip_size
        pdb.gimp_image_resize(img, new_width, new_height, -clip_size,
                              -clip_size)
        pdb.gimp_layer_resize(drawable, new_width, new_height, -clip_size,
                              -clip_size)

    pdb.file_png_save(img, drawable, os.path.join(output_folder, file_name),
                      file_name, 0, 9, 1, 0, 0, 1, 1)

    pdb.gimp_undo_push_group_end(img)

def prepare_makeplayingcards_folder(input_folder, output_folder):
    """ Prepare a folder of images for MakePlayingCards printing.
    """
    gimp.progress_init(
        'Prepare a folder of images for MakePlayingCards printing...')

    for file_name in os.listdir(input_folder):
        if not (file_name.endswith('.png') or file_name.endswith('.jpg')):
            continue

        img = pdb.gimp_file_load(os.path.join(input_folder, file_name),
                                 file_name)
        drawable = img.layers[0]
        pdb.python_prepare_makeplayingcards(img, drawable, output_folder)

register(
    'python_prepare_makeplayingcards',
    'Prepare an image for MakePlayingCards printing',
    '1. Rotate a landscape image. 2. Clip bleed margins. 3. Export PNG.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare MakePlayingCards',
    '*',
    [
        (PF_IMAGE, 'image', 'Input image', None),
        (PF_DRAWABLE, 'drawable', 'Input drawable', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_makeplayingcards,
    menu='<Image>/Filters')

register(
    'python_prepare_makeplayingcards_folder',
    'Prepare a folder of images for MakePlayingCards printing',
    '1. Rotate a landscape image. 2. Clip bleed margins. 3. Export PNG.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare MakePlayingCards Folder',
    '*',
    [
        (PF_DIRNAME, 'input_folder', 'Input folder', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_makeplayingcards_folder,
    menu='<Image>/Filters')

main()
