# -*- coding: utf8 -*-
""" Various common utils.
"""
import re


CHUNK_LIMIT = 1980
CHUNK_STATE = {
    ('', 'b'): 'b',
    ('', 'i'): 'i',
    ('b', 'b'): '',
    ('b', 'i'): 'bi',
    ('i', 'b'): 'ib',
    ('i', 'i'): '',
    ('bi', 'b'): '',
    ('bi', 'i'): 'b',
    ('ib', 'b'): 'i',
    ('ib', 'i'): ''
}
CHUNK_MISSING = {
    '': '',
    'b': '**',
    'i': '*',
    'bi': '***',
    'ib': '***'
}


def split_result(value):  # pylint: disable=R0912
    """ Split result into chunks.
    """
    chunks = []
    chunk = ''
    for line in value.split('\n'):
        if len(chunk + line) + 1 <= CHUNK_LIMIT:
            chunk += line + '\n'
        else:
            while len(chunk) > CHUNK_LIMIT:
                pos = chunk[:CHUNK_LIMIT].rfind(' ')
                if pos == -1:
                    pos = CHUNK_LIMIT - 1

                chunks.append(chunk[:pos + 1])
                chunk = chunk[pos + 1:]

            chunks.append(chunk)
            chunk = line + '\n'

    chunks.append(chunk)

    for i in range(len(chunks) - 1):
        cnt = chunks[i].count('```')
        if cnt % 2 == 0:
            continue

        if chunks[i].split('```')[-1].startswith('diff'):
            chunks[i + 1] = '```diff\n' + chunks[i + 1]
        else:
            chunks[i + 1] = '```\n' + chunks[i + 1]

        chunks[i] += '```\n'

    chunks = [chunk.replace('```diff\n```', '').replace('```\n```', '')
           for chunk in chunks]

    for i, chunk in enumerate(chunks):
        state = ''
        pos = 0
        while pos < len(chunk):
            char = chunk[pos]
            pos += 1
            if char == '*':
                if (pos < len(chunk) and chunk[pos] == '*' and
                        state not in ('bi', 'i')):
                    char = 'b'
                    pos += 1
                else:
                    char = 'i'

                state = CHUNK_STATE[(state, char)]

        missing = CHUNK_MISSING[state]
        chunks[i] = chunks[i] + missing
        if i < len(chunks) - 1:
            chunks[i + 1] = missing + chunks[i + 1]

    chunks = [re.sub(r'(\n+)(\*+)$', '\\2\\1',
                     re.sub(r'^(\*+)(\n+)', '\\2\\1', chunk))
              for chunk in chunks]

    return chunks
