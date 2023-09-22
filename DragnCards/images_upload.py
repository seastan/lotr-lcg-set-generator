# pylint: disable=C0209
""" Upload new images to S3.

See requirements in imagesUpload.sh.
"""
import logging
import os
import time

import boto3


DATA_PATH = 'images_upload.txt'
IMAGES_FOLDER = '/mnt/volume_postgres/cards/English/'
LOG_PATH = 'images_upload.log'
LOG_LIMIT = 5000

S3_BUCKET = 'dragncards-lotrlcg'
S3_PATH = 'cards/English/'


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')


def main():
    """ Main function.
    """
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as obj:
            old_timestamp = int(obj.read())
    except Exception:  # pylint: disable=W0703
        old_timestamp = 0

    try:
        s3_client = None
        timestamp = int(time.time())
        for _, _, filenames in os.walk(IMAGES_FOLDER):
            for filename in filenames:
                if not filename.endswith('.jpg'):
                    continue

                image_path = os.path.join(IMAGES_FOLDER, filename)
                mtime = int(os.path.getmtime(image_path)) + 1
                if mtime < old_timestamp:
                    continue

                if not s3_client:
                    s3_client = boto3.client('s3')

                s3_client.upload_file(
                    Filename=image_path,
                    Bucket=S3_BUCKET,
                    Key='{}{}'.format(S3_PATH, filename)
                )
                logging.info('Uploaded %s to S3 bucket', image_path)

            break

        with open(DATA_PATH, 'w', encoding='utf-8') as obj:
            obj.write(str(timestamp))
    except Exception as exc:  # pylint: disable=W0703
        message = 'Script failed: {}: {}'.format(
            type(exc).__name__, str(exc))[:LOG_LIMIT]
        logging.exception(message)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
