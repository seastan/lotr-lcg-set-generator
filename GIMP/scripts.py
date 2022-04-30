# pylint: disable=C0302
#!/usr/bin/env python
""" Custom GIMP plugin(s).
"""
import json
import math
import os
import re

from gimpfu import (gimp, pdb, register, main, PF_DIRNAME, PF_DRAWABLE,
                    PF_FILENAME, PF_IMAGE, ROTATE_90, ROTATE_270)


def _get_filename_backside(img, file_type='png'):
    """ Determine card side and output file name.
    """
    file_name = pdb.gimp_image_get_filename(img)
    file_name = os.path.split(file_name)[-1]
    file_name = '.'.join(file_name.split('.')[:-1])
    back_side = file_name.endswith('-Back-Face') or file_name.endswith('-2')
    file_name = file_name + '.' + file_type
    return (file_name, back_side)


def _get_rotation(drawable):
    """ Determine whether an image should be rotated or not.
    """
    rotation = ((drawable.width == 1050 and drawable.height == 750)
                or (drawable.width == 1126 and drawable.height == 826)
                or (drawable.width == 1680 and drawable.height == 1200)
                or (drawable.width == 1800 and drawable.height == 1320)
                or (drawable.width == 1801 and drawable.height == 1321)
                or (drawable.width == 2100 and drawable.height == 1500)
                or (drawable.width == 2250 and drawable.height == 1650)
                or (drawable.width == 2252 and drawable.height == 1652)
                or (drawable.width == 2800 and drawable.height == 2000)
                or (drawable.width == 3000 and drawable.height == 2200)
                or (drawable.width == 3002 and drawable.height == 2202)
                or (drawable.width == 4200 and drawable.height == 3000)
                or (drawable.width == 4500 and drawable.height == 3300)
                or (drawable.width == 4504 and drawable.height == 3304))
    return rotation


def _get_bleed_margin_size(drawable):
    """ Determine bleed margin size.
    """
    if ((drawable.width == 826 and drawable.height == 1126)
            or (drawable.width == 1126 and drawable.height == 826)):
        size = 38
    elif ((drawable.width == 1320 and drawable.height == 1800)
          or (drawable.width == 1800 and drawable.height == 1320)):
        size = 60
    elif ((drawable.width == 1321 and drawable.height == 1801)
          or (drawable.width == 1801 and drawable.height == 1321)):
        size = 60.5
    elif ((drawable.width == 1650 and drawable.height == 2250)
          or (drawable.width == 2250 and drawable.height == 1650)):
        size = 75
    elif ((drawable.width == 1652 and drawable.height == 2252)
          or (drawable.width == 2252 and drawable.height == 1652)):
        size = 76
    elif ((drawable.width == 2200 and drawable.height == 3000)
          or (drawable.width == 3000 and drawable.height == 2200)):
        size = 100
    elif ((drawable.width == 2202 and drawable.height == 3002)
          or (drawable.width == 3002 and drawable.height == 2202)):
        size = 101
    elif ((drawable.width == 3300 and drawable.height == 4500)
          or (drawable.width == 4500 and drawable.height == 3300)):
        size = 150
    elif ((drawable.width == 3304 and drawable.height == 4504)
          or (drawable.width == 4504 and drawable.height == 3304)):
        size = 152
    else:
        size = 0

    return size


def _get_pdf_clip_size(drawable):
    """ Determine PDF clip size.
    """
    if ((drawable.width == 826 and drawable.height == 1126)
            or (drawable.width == 1126 and drawable.height == 826)):
        size = 0.5
    elif ((drawable.width == 1650 and drawable.height == 2250)
          or (drawable.width == 2250 and drawable.height == 1650)):
        size = 0.5
    elif ((drawable.width == 1652 and drawable.height == 2252)
          or (drawable.width == 2252 and drawable.height == 1652)):
        size = 1
    elif ((drawable.width == 2200 and drawable.height == 3000)
          or (drawable.width == 3000 and drawable.height == 2200)):
        size = 0
    elif ((drawable.width == 2202 and drawable.height == 3002)
          or (drawable.width == 3002 and drawable.height == 2202)):
        size = 1
    elif ((drawable.width == 3300 and drawable.height == 4500)
          or (drawable.width == 4500 and drawable.height == 3300)):
        size = 0
    elif ((drawable.width == 3304 and drawable.height == 4504)
          or (drawable.width == 4504 and drawable.height == 3304)):
        size = 2
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
    elif ((drawable.width == 3000 and drawable.height == 4200)
          or (drawable.width == 4200 and drawable.height == 3000)):
        size = 150
    else:
        size = 0

    return size


def _get_mpc_clip_size(drawable):
    """ Determine MakePlayingCards clip size.
    """
    if ((drawable.width == 826 and drawable.height == 1126)
            or (drawable.width == 1126 and drawable.height == 826)):
        size = 2
    elif ((drawable.width == 1650 and drawable.height == 2250)
          or (drawable.width == 2250 and drawable.height == 1650)):
        size = 3
    elif ((drawable.width == 1652 and drawable.height == 2252)
          or (drawable.width == 2252 and drawable.height == 1652)):
        size = 4
    elif ((drawable.width == 2200 and drawable.height == 3000)
          or (drawable.width == 3000 and drawable.height == 2200)):
        size = 4
    elif ((drawable.width == 2202 and drawable.height == 3002)
          or (drawable.width == 3002 and drawable.height == 2202)):
        size = 5
    elif ((drawable.width == 3300 and drawable.height == 4500)
          or (drawable.width == 4500 and drawable.height == 3300)):
        size = 6
    elif ((drawable.width == 3304 and drawable.height == 4504)
          or (drawable.width == 4504 and drawable.height == 3304)):
        size = 8
    else:
        size = 0

    return size


def _get_dtc_clip_size(drawable):
    """ Determine DriveThruCards clip size.
    """
    if ((drawable.width == 826 and drawable.height == 1126)
            or (drawable.width == 1126 and drawable.height == 826)):
        size = 0.5
    elif ((drawable.width == 1650 and drawable.height == 2250)
          or (drawable.width == 2250 and drawable.height == 1650)):
        size = 0
    elif ((drawable.width == 1652 and drawable.height == 2252)
          or (drawable.width == 2252 and drawable.height == 1652)):
        size = 1
    elif ((drawable.width == 2200 and drawable.height == 3000)
          or (drawable.width == 3000 and drawable.height == 2200)):
        size = 0
    elif ((drawable.width == 2202 and drawable.height == 3002)
          or (drawable.width == 3002 and drawable.height == 2202)):
        size = 1
    elif ((drawable.width == 3300 and drawable.height == 4500)
          or (drawable.width == 4500 and drawable.height == 3300)):
        size = 0
    elif ((drawable.width == 3304 and drawable.height == 4504)
          or (drawable.width == 4504 and drawable.height == 3304)):
        size = 2
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
        if not (file_name.endswith('.png') or file_name.endswith('.jpg')
                or file_name.endswith('.tif')):
            continue

        img = pdb.gimp_file_load(os.path.join(input_folder, file_name),
                                 file_name)
        drawable = img.layers[0]
        func(img, drawable, output_folder)


def cut_bleed_margins(img, drawable, output_folder):
    """ Cut bleed margins from an image.
    """
    gimp.progress_init('Cut bleed margins from an image...')
    pdb.gimp_undo_push_group_start(img)

    try:
        file_name, _ = _get_filename_backside(img)
    except Exception:  # pylint: disable=W0703
        pdb.gimp_undo_push_group_end(img)
        return

    clip_size = _get_bleed_margin_size(drawable)
    if clip_size:
        _clip(img, drawable, clip_size, False)

    pdb.file_png_save(img, drawable,
                      os.path.join(output_folder, file_name), file_name,
                      0, 9, 1, 0, 0, 1, 1)
    pdb.gimp_undo_push_group_end(img)


def prepare_db_output(img, drawable, output_folder):
    """ Prepare an image for DB output.
    """
    gimp.progress_init('Prepare an image for DB output...')
    pdb.gimp_undo_push_group_start(img)

    try:
        file_name, _ = _get_filename_backside(img)
    except Exception:  # pylint: disable=W0703
        pdb.gimp_undo_push_group_end(img)
        return

    pdb.script_fu_round_corners(img, drawable, 40, 0, 0, 0, 0, 0, 0)

    pdb.file_png_save(img, drawable,
                      os.path.join(output_folder, file_name), file_name,
                      0, 9, 1, 0, 0, 1, 1)
    pdb.gimp_undo_push_group_end(img)


def prepare_pdf_front_old(img, drawable, output_folder):
    """ Prepare a front image for PDF document. [OLD VERSION]
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

    if margin_size:
        _add_margin(img, drawable, margin_size)

    clip_size = _get_pdf_clip_size(drawable)
    if clip_size:
        _clip(img, drawable, clip_size, rotation and back_side)

    pdb.file_png_save(img, drawable,
                      os.path.join(output_folder, file_name), file_name,
                      0, 9, 1, 0, 0, 1, 1)
    pdb.gimp_undo_push_group_end(img)


def prepare_pdf_front(img, drawable, output_folder):
    """ Prepare a front image for PDF document. [NEW VERSION]
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
    clip_size = _get_pdf_clip_size(drawable)

    if rotation:
        _rotate(drawable, back_side)

    if clip_size:
        _clip(img, drawable, clip_size, rotation and back_side)

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
    clip_size = _get_pdf_clip_size(drawable)

    if rotation:
        _rotate(drawable, back_side)

    if clip_size:
        _clip(img, drawable, clip_size, rotation and back_side)

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

    pdb.gimp_drawable_brightness_contrast(drawable, 0.1, 0.0)

    pdb.file_png_save(img, drawable,
                      os.path.join(output_folder, file_name), file_name,
                      0, 9, 1, 0, 0, 1, 1)
    pdb.gimp_undo_push_group_end(img)


def prepare_drivethrucards_jpg(img, drawable, output_folder):
    """ Prepare a JPG image for DriveThruCards printing.
    """
    gimp.progress_init('Prepare a JPG image for DriveThruCards printing...')
    pdb.gimp_undo_push_group_start(img)

    try:
        file_name, back_side = _get_filename_backside(img, 'jpg')
    except Exception:  # pylint: disable=W0703
        pdb.gimp_undo_push_group_end(img)
        return

    rotation = _get_rotation(drawable)
    clip_size = _get_dtc_clip_size(drawable)

    if rotation:
        _rotate(drawable, back_side)

    if clip_size:
        _clip(img, drawable, clip_size, rotation and back_side)

    pdb.file_jpeg_save(img, drawable,
                       os.path.join(output_folder, file_name), file_name,
                       1, 0, 1, 0, '', 2, 1, 0, 0)
    pdb.gimp_undo_push_group_end(img)


def prepare_drivethrucards_tif(img, drawable, output_folder):
    """ Prepare a TIFF image for DriveThruCards printing.
    """
    gimp.progress_init('Prepare a TIFF image for DriveThruCards printing...')
    pdb.gimp_undo_push_group_start(img)

    try:
        file_name, back_side = _get_filename_backside(img, 'tif')
    except Exception:  # pylint: disable=W0703
        pdb.gimp_undo_push_group_end(img)
        return

    rotation = _get_rotation(drawable)
    clip_size = _get_dtc_clip_size(drawable)

    if rotation:
        _rotate(drawable, back_side)

    if clip_size:
        _clip(img, drawable, clip_size, rotation and back_side)

    pdb.file_tiff_save(img, drawable,
                       os.path.join(output_folder, file_name), file_name, 1)
    pdb.gimp_undo_push_group_end(img)


def prepare_mbprint_jpg(img, drawable, output_folder):
    """ Prepare a JPG image for MBPrint printing.
    """
    gimp.progress_init('Prepare a JPG image for MBPrint printing...')
    pdb.gimp_undo_push_group_start(img)

    try:
        file_name, back_side = _get_filename_backside(img, 'jpg')
    except Exception:  # pylint: disable=W0703
        pdb.gimp_undo_push_group_end(img)
        return

    rotation = _get_rotation(drawable)
    if rotation:
        _rotate(drawable, back_side)

    pdb.file_jpeg_save(img, drawable,
                       os.path.join(output_folder, file_name), file_name,
                       1, 0, 1, 0, '', 2, 1, 0, 0)
    pdb.gimp_undo_push_group_end(img)


def prepare_generic_png(img, drawable, output_folder):
    """ Prepare a generic PNG image.
    """
    gimp.progress_init('Prepare a generic PNG image...')
    pdb.gimp_undo_push_group_start(img)

    try:
        file_name, back_side = _get_filename_backside(img, 'png')
    except Exception:  # pylint: disable=W0703
        pdb.gimp_undo_push_group_end(img)
        return

    rotation = _get_rotation(drawable)
    if rotation:
        _rotate(drawable, back_side)

    pdb.file_png_save(img, drawable,
                      os.path.join(output_folder, file_name), file_name,
                      0, 9, 1, 0, 0, 1, 1)
    pdb.gimp_undo_push_group_end(img)


def prepare_tts(img, _, output_folder):  # pylint: disable=R0914
    """ Prepare a TTS sheet image.
    """
    gimp.progress_init('Prepare a TTS sheet image...')
    pdb.gimp_undo_push_group_start(img)

    try:
        file_name, _ = _get_filename_backside(img, 'jpg')
    except Exception:  # pylint: disable=W0703
        pdb.gimp_undo_push_group_end(img)
        return

    parts = file_name.split('_')
    num = int(parts[-3])
    rows = int(parts[-4])
    columns = int(parts[-5])
    new_width = columns * 750
    new_height = rows * 1050
    pdb.gimp_image_scale(img, new_width, new_height)

    json_path = re.sub(r'\.jpg$', '.json', pdb.gimp_image_get_filename(img))
    try:
        with open(json_path, 'r') as fobj:
            cards = json.load(fobj)
    except Exception:  # pylint: disable=W0703
        pdb.gimp_undo_push_group_end(img)
        return

    cards = [c['path'] for c in cards]
    if len(cards) != num:
        pdb.gimp_undo_push_group_end(img)
        return

    card_rows = [cards[i * columns:(i + 1) * columns]
                 for i in range((len(cards) + columns - 1) // columns)]
    if len(card_rows) != rows:
        pdb.gimp_undo_push_group_end(img)
        return

    for i, card_row in enumerate(card_rows):
        for j, card_path in enumerate(card_row):
            if not os.path.exists(card_path):
                pdb.gimp_undo_push_group_end(img)
                return

            card_layer = pdb.gimp_file_load_layer(img, card_path)
            pdb.gimp_image_insert_layer(img, card_layer, None, -1)
            rotation = _get_rotation(card_layer)
            if rotation:
                _rotate(card_layer, True)

            pdb.gimp_layer_set_offsets(card_layer, j * 750, i * 1050)
            pdb.gimp_image_merge_down(img, card_layer, 1)

    pdb.file_jpeg_save(img, img.layers[0],
                       os.path.join(output_folder, file_name), file_name,
                       1, 0, 1, 0, '', 2, 1, 0, 0)
    pdb.gimp_undo_push_group_end(img)


def generate_renderer_artwork(json_path, output_folder):  # pylint: disable=R0914,R0915
    """ Generate artwork for DragnCards proxy images.
    """
    gimp.progress_init('Generate artwork for DragnCards proxy images...')

    portrait = {}
    portrait['Ally'] = '87,0,326,330'
    portrait['Attachment'] = '40,50,333,280'
    portrait['Campaign'] = '0,0,413,245'
    portrait['Contract'] = '0,0,413,315'
    portrait['Encounter Side Quest'] = '0,0,563,413'
    portrait['Enemy'] = '87,0,326,330'
    portrait['Event'] = '60,0,353,330'
    portrait['Hero'] = '87,0,326,330'
    portrait['Location'] = '0,60,413,268'
    portrait['Nightmare'] = '0,77,413,245'
    portrait['Objective'] = '0,69,413,300'
    portrait['Objective Ally'] = '78,81,335,268'
    portrait['Objective Hero'] = '78,81,335,268'
    portrait['Objective Location'] = '0,69,413,300'
    portrait['Player Objective'] = '0,69,413,300'
    portrait['Player Side Quest'] = '0,0,563,413'
    portrait['Quest'] = '0,0,563,413'
    portrait['Ship Enemy'] = '87,0,326,330'
    portrait['Ship Objective'] = '78,81,335,268'
    portrait['Treachery'] = '60,0,353,330'
    portrait['Treasure'] = '0,61,413,265'

    for card_type in portrait:
        values = portrait[card_type].split(',')
        portrait[card_type] = (float(round(int(values[2]) * 2 / 1.75)),
                               float(round(int(values[3]) * 2 / 1.75)))

    try:
        with open(json_path, 'r') as fobj:
            images = json.load(fobj)
    except Exception:  # pylint: disable=W0703
        return

    for card_id, data in images.items():
        if data['card_type'] not in portrait:
            return

        img = pdb.gimp_file_load(data['path'],
                                 os.path.split(data['path'])[-1])
        drawable = img.layers[0]
        image_width = drawable.width
        image_height = drawable.height

        img = pdb.gimp_file_load(os.path.join('GIMP', 'black.png'),
                                 'black.png')
        pdb.gimp_image_scale(img, image_width, image_height)

        layer = pdb.gimp_file_load_layer(img, data['path'])
        pdb.gimp_image_insert_layer(img, layer, None, -1)
        pdb.gimp_layer_set_offsets(layer, 0, 0)
        pdb.gimp_image_merge_down(img, layer, 1)
        drawable = img.layers[0]

        portrait_width = portrait[data['card_type']][0]
        portrait_height = portrait[data['card_type']][1]
        scale = float(data['scale'])
        if scale == 0:
            if (image_height * (portrait_width / image_width) /
                    portrait_height >= 1):
                scale = portrait_width / image_width
            else:
                scale = portrait_height / image_height
        else:
            scale = (scale * 2 / 1.75) / 100

        image_width = round(image_width * scale)
        image_height = round(image_height * scale)
        pdb.gimp_image_scale(img, image_width, image_height)

        new_width = image_width + 2 * portrait_width
        new_height = image_height + 2 * portrait_height
        pdb.gimp_image_resize(img, new_width, new_height, portrait_width,
                              portrait_height)
        pdb.gimp_layer_resize(drawable, new_width, new_height, portrait_width,
                              portrait_height)

        left = round((image_width - portrait_width) / 2 + portrait_width -
                     float(data['panx']) * 2 / 1.75)
        top = round((image_height - portrait_height) / 2 + portrait_height -
                    float(data['pany']) * 2 / 1.75)
        #print('%s: image: %s/%s, portrait: %s/%s, left/top: %s/%s' %
        #      (card_id, image_width, image_height, portrait_width,
        #       portrait_height, left, top))
        pdb.gimp_image_resize(img, portrait_width, portrait_height, -left,
                              -top)
        pdb.gimp_layer_resize(drawable, portrait_width, portrait_height,
                              -left, -top)

        output_file = '%s.jpg' % (card_id,)
        pdb.file_jpeg_save(img, drawable,
                           os.path.join(output_folder, output_file),
                           output_file, 0.9, 0, 1, 0, '', 2, 1, 0, 0)


def generate_renderer_custom_image(img, drawable, output_folder):
    """ Generate a custom image for DragnCards proxy images.
    """
    gimp.progress_init('Generate a custom image for DragnCards proxy '
                       'images...')
    pdb.gimp_undo_push_group_start(img)

    if drawable.width > 362:
        scale = 362.0 / drawable.width
        image_width = 362
        image_height = round(drawable.height * scale)
        pdb.gimp_image_scale(img, image_width, image_height)

        file_name = pdb.gimp_image_get_filename(img)
        if file_name.endswith('.png'):
            pdb.file_png_save(img, drawable,
                              os.path.join(output_folder, file_name),
                              file_name, 0, 9, 1, 0, 0, 1, 1)
        else:
            pdb.file_jpeg_save(img, drawable,
                               os.path.join(output_folder, file_name),
                               file_name, 0.9, 0, 1, 0, '', 2, 1, 0, 0)

    pdb.gimp_undo_push_group_end(img)


def cut_bleed_margins_folder(input_folder, output_folder):
    """ Cut bleed margins from a folder of images.
    """
    gimp.progress_init(
        'Cut bleed margins from a folder of images...')
    _iterate_folder(input_folder, output_folder, cut_bleed_margins)


def prepare_db_output_folder(input_folder, output_folder):
    """ Prepare a folder of images for DB output.
    """
    gimp.progress_init(
        'Prepare a folder of images for DB output...')
    _iterate_folder(input_folder, output_folder, prepare_db_output)


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


def prepare_drivethrucards_jpg_folder(input_folder, output_folder):
    """ Prepare a folder of images for DriveThruCards printing (JPG).
    """
    gimp.progress_init(
        'Prepare a folder of images for DriveThruCards printing (JPG)...')
    _iterate_folder(input_folder, output_folder, prepare_drivethrucards_jpg)


def prepare_drivethrucards_tif_folder(input_folder, output_folder):
    """ Prepare a folder of images for DriveThruCards printing (TIFF).
    """
    gimp.progress_init(
        'Prepare a folder of images for DriveThruCards printing (TIFF)...')
    _iterate_folder(input_folder, output_folder, prepare_drivethrucards_tif)


def prepare_mbprint_jpg_folder(input_folder, output_folder):
    """ Prepare a folder of images for MBPrint printing (JPG).
    """
    gimp.progress_init(
        'Prepare a folder of images for MBPrint printing (JPG)...')
    _iterate_folder(input_folder, output_folder, prepare_mbprint_jpg)


def prepare_generic_png_folder(input_folder, output_folder):
    """ Prepare a folder of generic PNG images.
    """
    gimp.progress_init(
        'Prepare a folder of generic PNG images...')
    _iterate_folder(input_folder, output_folder, prepare_generic_png)


def prepare_tts_folder(input_folder, output_folder):
    """ Prepare a folder of TTS sheet images.
    """
    gimp.progress_init(
        'Prepare a folder of TTS sheet images...')
    _iterate_folder(input_folder, output_folder, prepare_tts)


def generate_renderer_custom_image_folder(input_folder, output_folder):
    """ Generate a folder of custom images for DragnCards proxy images.
    """
    gimp.progress_init(
        'Generate a folder of custom images for DragnCards proxy images...')
    _iterate_folder(input_folder, output_folder,
                    generate_renderer_custom_image)


register(
    'python_cut_bleed_margins',
    'Cut bleed margins from an image',
    '1. Cut bleed margins. 2. Export PNG.',
    'A.R.',
    'A.R.',
    '2020',
    'Cut Bleed Margins',
    '*',
    [
        (PF_IMAGE, 'image', 'Input image', None),
        (PF_DRAWABLE, 'drawable', 'Input drawable', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    cut_bleed_margins,
    menu='<Image>/Filters')

register(
    'python_cut_bleed_margins_folder',
    'Cut bleed margins from a folder of images',
    '1. Cut bleed margins. 2. Export PNG.',
    'A.R.',
    'A.R.',
    '2020',
    'Cut Bleed Margins Folder',
    '*',
    [
        (PF_DIRNAME, 'input_folder', 'Input folder', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    cut_bleed_margins_folder,
    menu='<Image>/Filters')

register(
    'python_prepare_db_output',
    'Prepare an image for DB output',
    '1. Make round corners. 2. Export PNG.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare DB Output',
    '*',
    [
        (PF_IMAGE, 'image', 'Input image', None),
        (PF_DRAWABLE, 'drawable', 'Input drawable', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_db_output,
    menu='<Image>/Filters')

register(
    'python_prepare_db_output_folder',
    'Prepare a folder of images for DB output',
    '1. Make round corners. 2. Export PNG.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare DB Output Folder',
    '*',
    [
        (PF_DIRNAME, 'input_folder', 'Input folder', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_db_output_folder,
    menu='<Image>/Filters')

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
    '1. Rotate a landscape image. 2. Remove redundant bleed margins. 3. Export PNG.',
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
    '1. Rotate a landscape image. 2. Remove redundant bleed margins. 3. Export PNG.',
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
    '1. Rotate a landscape image. 2. Clip bleed margins. 3. Adjust brightness/contrast. '
        '4. Export PNG.',
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
    '1. Rotate a landscape image. 2. Clip bleed margins. 3. Adjust brightness/contrast. '
        '4. Export PNG.',
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
    'python_prepare_drivethrucards_jpg',
    'Prepare a JPG image for DriveThruCards printing',
    '1. Rotate a landscape image. 2. Clip bleed margins. 3. Export JPG.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare DriveThruCards JPG',
    '*',
    [
        (PF_IMAGE, 'image', 'Input image', None),
        (PF_DRAWABLE, 'drawable', 'Input drawable', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_drivethrucards_jpg,
    menu='<Image>/Filters')

register(
    'python_prepare_drivethrucards_jpg_folder',
    'Prepare a folder of images for DriveThruCards printing (JPG)',
    '1. Rotate a landscape image. 2. Clip bleed margins. 3. Export JPG.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare DriveThruCards JPG Folder',
    '*',
    [
        (PF_DIRNAME, 'input_folder', 'Input folder', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_drivethrucards_jpg_folder,
    menu='<Image>/Filters')

register(
    'python_prepare_drivethrucards_tif',
    'Prepare a TIFF image for DriveThruCards printing',
    '1. Rotate a landscape image. 2. Clip bleed margins. 3. Export TIFF.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare DriveThruCards TIFF',
    '*',
    [
        (PF_IMAGE, 'image', 'Input image', None),
        (PF_DRAWABLE, 'drawable', 'Input drawable', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_drivethrucards_tif,
    menu='<Image>/Filters')

register(
    'python_prepare_drivethrucards_tif_folder',
    'Prepare a folder of images for DriveThruCards printing (TIFF)',
    '1. Rotate a landscape image. 2. Clip bleed margins. 3. Export TIFF.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare DriveThruCards TIFF Folder',
    '*',
    [
        (PF_DIRNAME, 'input_folder', 'Input folder', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_drivethrucards_tif_folder,
    menu='<Image>/Filters')

register(
    'python_prepare_mbprint_jpg',
    'Prepare a JPG image for MBPrint printing',
    '1. Rotate a landscape image. 2. Export JPG.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare MBPrint JPG',
    '*',
    [
        (PF_IMAGE, 'image', 'Input image', None),
        (PF_DRAWABLE, 'drawable', 'Input drawable', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_mbprint_jpg,
    menu='<Image>/Filters')

register(
    'python_prepare_mbprint_jpg_folder',
    'Prepare a folder of images for MBPrint printing (JPG)',
    '1. Rotate a landscape image. 2. Export JPG.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare MBPrint JPG Folder',
    '*',
    [
        (PF_DIRNAME, 'input_folder', 'Input folder', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_mbprint_jpg_folder,
    menu='<Image>/Filters')

register(
    'python_prepare_generic_png',
    'Prepare a generic PNG image',
    '1. Rotate a landscape image. 2. Export PNG.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare Generic PNG',
    '*',
    [
        (PF_IMAGE, 'image', 'Input image', None),
        (PF_DRAWABLE, 'drawable', 'Input drawable', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_generic_png,
    menu='<Image>/Filters')

register(
    'python_prepare_generic_png_folder',
    'Prepare a folder of generic PNG images',
    '1. Rotate a landscape image. 2. Export PNG.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare Generic PNG Folder',
    '*',
    [
        (PF_DIRNAME, 'input_folder', 'Input folder', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_generic_png_folder,
    menu='<Image>/Filters')

register(
    'python_prepare_tts',
    'Prepare a TTS sheet image',
    'Combine individual images into a TTS sheet.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare TTS',
    '*',
    [
        (PF_IMAGE, 'image', 'Input image', None),
        (PF_DRAWABLE, 'drawable', 'Input drawable', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_tts,
    menu='<Image>/Filters')

register(
    'python_prepare_tts_folder',
    'Prepare a folder of TTS sheet images',
    'Combine individual images into TTS sheets.',
    'A.R.',
    'A.R.',
    '2020',
    'Prepare TTS Folder',
    '*',
    [
        (PF_DIRNAME, 'input_folder', 'Input folder', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    prepare_tts_folder,
    menu='<Image>/Filters')

register(
    'python_generate_renderer_artwork',
    'Generate artwork for DragnCards proxy images',
    'Scale, crop and export as JPG each of the input images.',
    'A.R.',
    'A.R.',
    '2020',
    'Generate Renderer Artwork',
    '*',
    [
        (PF_FILENAME, 'json_path', 'JSON file', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    generate_renderer_artwork,
    menu='<Image>/Filters')

register(
    'python_generate_renderer_custom_image',
    'Generate a custom image for DragnCards proxy images',
    'Scale the image.',
    'A.R.',
    'A.R.',
    '2020',
    'Generate Renderer Custom Image',
    '*',
    [
        (PF_IMAGE, 'image', 'Input image', None),
        (PF_DRAWABLE, 'drawable', 'Input drawable', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    generate_renderer_custom_image,
    menu='<Image>/Filters')

register(
    'python_generate_renderer_custom_image_folder',
    'Generate a folder of custom images for DragnCards proxy images',
    'Scale the image.',
    'A.R.',
    'A.R.',
    '2020',
    'Generate Renderer Custom Image Folder',
    '*',
    [
        (PF_DIRNAME, 'input_folder', 'Input folder', None),
        (PF_DIRNAME, 'output_folder', 'Output folder', None)
    ],
    [],
    generate_renderer_custom_image_folder,
    menu='<Image>/Filters')

main()
