#!/usr/bin/env python
""" Custom GIMP plugin(s).
"""
import math
import os
from gimpfu import (gimp, pdb, register, main, PF_IMAGE, PF_DRAWABLE,
                    PF_DIRNAME, ROTATE_90, ROTATE_270)


def _get_filename_backside(img):
    """ Determine card side and output file name.
    """
    file_name = pdb.gimp_image_get_filename(img)
    file_name = os.path.split(file_name)[-1]
    file_name = '.'.join(file_name.split('.')[:-1])
    back_side = file_name.endswith('-Back-Face') or file_name.endswith('-2')
    file_name = file_name + '.png'
    return (file_name, back_side)


def _get_rotation(drawable):
    """ Determine whether an image should be rotated or not.
    """
    rotation = ((drawable.width == 1050 and drawable.height == 750)
                or (drawable.width == 1126 and drawable.height == 826)
                or (drawable.width == 2100 and drawable.height == 1500)
                or (drawable.width == 2250 and drawable.height == 1650)
                or (drawable.width == 2800 and drawable.height == 2000)
                or (drawable.width == 3000 and drawable.height == 2200))
    return rotation


def _get_mpc_clip_size(drawable):
    """ Determine MakePlayingCards clip size.
    """
    if ((drawable.width == 826 and drawable.height == 1126)
            or (drawable.width == 1126 and drawable.height == 826)):
        size = 2
    elif ((drawable.width == 1650 and drawable.height == 2250)
          or (drawable.width == 2250 and drawable.height == 1650)):
        size = 3
    elif ((drawable.width == 2200 and drawable.height == 3000)
          or (drawable.width == 3000 and drawable.height == 2200)):
        size = 4
    else:
        size = 0

    return size


def _get_dtc_clip_size(drawable):
    """ Determine MakePlayingCards clip size.
    """
    if ((drawable.width == 826 and drawable.height == 1126)
            or (drawable.width == 1126 and drawable.height == 826)):
        size = 0.5
    elif ((drawable.width == 1650 and drawable.height == 2250)
          or (drawable.width == 2250 and drawable.height == 1650)):
        size = 0
    elif ((drawable.width == 2200 and drawable.height == 3000)
          or (drawable.width == 3000 and drawable.height == 2200)):
        size = 0
    else:
        size = 0

    return size


def _get_pdf_margin_size(drawable):
    """ Determine PDF bleed margin size.
    """
    if ((drawable.width == 750 and drawable.height == 1050)
            or (drawable.width == 1050 and drawable.height == 750)):
        size = 38
    elif ((drawable.width == 1500 and drawable.height == 2100)
          or (drawable.width == 2100 and drawable.height == 1500)):
        size = 75
    elif ((drawable.width == 2000 and drawable.height == 2800)
          or (drawable.width == 2800 and drawable.height == 2000)):
        size = 100
    else:
        size = 0

    return size


def _rotate(drawable, back_side):
    """ Rotate an image.
    """
    if back_side:
        pdb.gimp_item_transform_rotate_simple(drawable, ROTATE_90, False,
                                              drawable.height / 2,
                                              drawable.height / 2)
    else:
        pdb.gimp_item_transform_rotate_simple(drawable, ROTATE_270, False,
                                              drawable.width / 2,
                                              drawable.width / 2)


def _clip(img, drawable, clip_size, rotated_back):
    """ Clip an image.
    """
    new_width = drawable.width - 2 * clip_size
    new_height = drawable.height - 2 * clip_size
    if rotated_back:
        off = -(math.floor(clip_size))
    else:
        off = -(math.ceil(clip_size))

    pdb.gimp_image_resize(img, new_width, new_height, off, off)
    pdb.gimp_layer_resize(drawable, new_width, new_height, off, off)


def _add_margin(img, drawable, size):
    """ Add bleed margin to an image.
    """
    if size:
        new_width = drawable.width + 2 * size
        new_height = drawable.height + 2 * size
        pdb.gimp_image_resize(img, new_width, new_height, size, size)
        pdb.gimp_layer_resize(drawable, new_width, new_height, size, size)


def _iterate_folder(input_folder, output_folder, func):
    """ Apply a given function to a folder of images.
    """
    for file_name in os.listdir(input_folder):
        if not (file_name.endswith('.png') or file_name.endswith('.jpg')):
            continue

        img = pdb.gimp_file_load(os.path.join(input_folder, file_name),
                                 file_name)
        drawable = img.layers[0]
        func(img, drawable, output_folder)


def prepare_pdf_front(img, drawable, output_folder):
    """ Prepare a front image for PDF document.
    """
    gimp.progress_init('Prepare a front image for PDF document...')
    pdb.gimp_undo_push_group_start(img)

    try:
        file_name, back_side = _get_filename_backside(img)
    except Exception:  # pylint: disable=W0703
        pdb.gimp_undo_push_group_end(img)
        return

    if back_side:
        pdb.gimp_undo_push_group_end(img)
        return

    rotation = _get_rotation(drawable)
    margin_size = _get_pdf_margin_size(drawable)

    if rotation:
        _rotate(drawable, back_side)

    _add_margin(img, drawable, margin_size)
    pdb.file_png_save(img, drawable,
                      os.path.join(output_folder, file_name), file_name,
                      0, 9, 1, 0, 0, 1, 1)
    pdb.gimp_undo_push_group_end(img)


def prepare_pdf_back(img, drawable, output_folder):
    """ Prepare a back image for PDF document.
    """
    gimp.progress_init('Prepare a back image for PDF document...')
    pdb.gimp_undo_push_group_start(img)

    try:
        file_name, back_side = _get_filename_backside(img)
    except Exception:  # pylint: disable=W0703
        pdb.gimp_undo_push_group_end(img)
        return

    if not back_side:
        pdb.gimp_undo_push_group_end(img)
        return

    rotation = _get_rotation(drawable)

    if rotation:
        _rotate(drawable, back_side)

    pdb.file_png_save(img, drawable,
                      os.path.join(output_folder, file_name), file_name,
                      0, 9, 1, 0, 0, 1, 1)
    pdb.gimp_undo_push_group_end(img)


def prepare_makeplayingcards(img, drawable, output_folder):
    """ Prepare an image for MakePlayingCards printing.
    """
    gimp.progress_init('Prepare an image for MakePlayingCards printing...')
    pdb.gimp_undo_push_group_start(img)

    try:
        file_name, back_side = _get_filename_backside(img)
    except Exception:  # pylint: disable=W0703
        pdb.gimp_undo_push_group_end(img)
        return

    rotation = _get_rotation(drawable)
    clip_size = _get_mpc_clip_size(drawable)

    if rotation:
        _rotate(drawable, back_side)

    if clip_size:
        _clip(img, drawable, clip_size, rotation and back_side)

    pdb.file_png_save(img, drawable,
                      os.path.join(output_folder, file_name), file_name,
                      0, 9, 1, 0, 0, 1, 1)
    pdb.gimp_undo_push_group_end(img)


def prepare_drivethrucards(img, drawable, output_folder):
    """ Prepare an image for DriveThruCards printing.
    """
    gimp.progress_init('Prepare an image for DriveThruCards printing...')
    pdb.gimp_undo_push_group_start(img)

    try:
        file_name, back_side = _get_filename_backside(img)
    except Exception:  # pylint: disable=W0703
        pdb.gimp_undo_push_group_end(img)
        return

    rotation = _get_rotation(drawable)
    clip_size = _get_dtc_clip_size(drawable)

    if rotation:
        _rotate(drawable, back_side)

    if clip_size:
        _clip(img, drawable, clip_size, rotation and back_side)

    pdb.file_png_save(img, drawable,
                      os.path.join(output_folder, file_name), file_name,
                      0, 9, 1, 0, 0, 1, 1)
    pdb.gimp_undo_push_group_end(img)


def prepare_pdf_front_folder(input_folder, output_folder):
    """ Prepare a folder of front images for PDF document.
    """
    gimp.progress_init(
        'Prepare a folder of front images for PDF document...')
    _iterate_folder(input_folder, output_folder, prepare_pdf_front)


def prepare_pdf_back_folder(input_folder, output_folder):
    """ Prepare a folder of back images for PDF document.
    """
    gimp.progress_init(
        'Prepare a folder of back images for PDF document...')
    _iterate_folder(input_folder, output_folder, prepare_pdf_back)


def prepare_makeplayingcards_folder(input_folder, output_folder):
    """ Prepare a folder of images for MakePlayingCards printing.
    """
    gimp.progress_init(
        'Prepare a folder of images for MakePlayingCards printing...')
    _iterate_folder(input_folder, output_folder, prepare_makeplayingcards)


def prepare_drivethrucards_folder(input_folder, output_folder):
    """ Prepare a folder of images for DriveThruCards printing.
    """
    gimp.progress_init(
        'Prepare a folder of images for DriveThruCards printing...')
    _iterate_folder(input_folder, output_folder, prepare_drivethrucards)


register(
    'python_prepare_pdf_front',
    'Prepare a front image for PDF document',
    '1. Rotate a landscape image. 2. Add white bleed margins. 3. Export PNG.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare PDF Front',
    '*',
    [
        (PF_IMAGE, 'image', 'Input image', None),
        (PF_DRAWABLE, 'drawable', 'Input drawable', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_pdf_front,
    menu='<Image>/Filters')

register(
    'python_prepare_pdf_front_folder',
    'Prepare a folder of front images for PDF document',
    '1. Rotate a landscape image. 2. Add white bleed margins. 3. Export PNG.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare PDF Front Folder',
    '*',
    [
        (PF_DIRNAME, 'input_folder', 'Input folder', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_pdf_front_folder,
    menu='<Image>/Filters')

register(
    'python_prepare_pdf_back',
    'Prepare a back image for PDF document',
    '1. Rotate a landscape image. 2. Export PNG.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare PDF Back',
    '*',
    [
        (PF_IMAGE, 'image', 'Input image', None),
        (PF_DRAWABLE, 'drawable', 'Input drawable', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_pdf_back,
    menu='<Image>/Filters')

register(
    'python_prepare_pdf_back_folder',
    'Prepare a folder of back images for PDF document',
    '1. Rotate a landscape image. 2. Export PNG.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare PDF Back Folder',
    '*',
    [
        (PF_DIRNAME, 'input_folder', 'Input folder', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_pdf_back_folder,
    menu='<Image>/Filters')

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

register(
    'python_prepare_drivethrucards',
    'Prepare an image for DriveThruCards printing',
    '1. Rotate a landscape image. 2. Clip bleed margins. 3. Export PNG.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare DriveThruCards',
    '*',
    [
        (PF_IMAGE, 'image', 'Input image', None),
        (PF_DRAWABLE, 'drawable', 'Input drawable', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_drivethrucards,
    menu='<Image>/Filters')

register(
    'python_prepare_drivethrucards_folder',
    'Prepare a folder of images for DriveThruCards printing',
    '1. Rotate a landscape image. 2. Clip bleed margins. 3. Export PNG.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare DriveThruCards Folder',
    '*',
    [
        (PF_DIRNAME, 'input_folder', 'Input folder', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_drivethrucards_folder,
    menu='<Image>/Filters')

main()
