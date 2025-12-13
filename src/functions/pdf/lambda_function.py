import logging
import os
import zlib

import pikepdf
from PIL import Image
from aws_lambda_typing import context as context_, events
from pikepdf import Name, PdfImage

from functions.common import s3_event_record_to_bucket_and_key, s3_download_object_to_file, s3_upload_file_to_bucket

logger = logging.getLogger(__name__)


def lambda_handler(event: events.S3Event, context: context_.Context) -> None:
    for record in event["Records"]:
        bucket, key = s3_event_record_to_bucket_and_key(record)

        logger.info(f"Processing {key} from bucket {bucket}.")

        file_name, file_ext = os.path.splitext(os.path.basename(key))
        tmp_file_in = f"/tmp/{os.path.basename(key)}"
        tmp_file_out = f"/tmp/compressed_{os.path.basename(key)}"

        logger.info(f"Downloading {key} from bucket {bucket} into {tmp_file_in}.")

        s3_download_object_to_file(bucket, key, tmp_file_in)

        logger.info(f"Compressing {key}.")

        compress_images_in_pdf(tmp_file_in, tmp_file_out)

        new_key = f"{file_name}_compressed{file_ext}"
        logger.info(f"Uploading compressed object {tmp_file_out} to bucket {bucket} with key {new_key}.")

        s3_upload_file_to_bucket(bucket, new_key, tmp_file_out)


# credits: ChatGPT
def compress_pil_image(pil_img, target_dpi=(72, 72), jpeg_quality=75, target_scale=72 / 300):
    # Resize the PIL image according to your scale (same logic as before)
    orig_w, orig_h = pil_img.size
    new_w = max(1, int(orig_w * target_scale))
    new_h = max(1, int(orig_h * target_scale))
    pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    if pil_img.mode in ("RGBA", "P"):
        pil_img = pil_img.convert("RGB")

    return pil_img


# credits: ChatGPT
def compress_images_in_pdf(input_path: str, output_path: str):
    with pikepdf.open(input_path) as pdf:
        # iterate pages
        for page_no, page in enumerate(pdf.pages):
            # page.images is a mapping of image names to PdfImage objects
            for name, pdfimageobj in page.images.items():
                pdfimage = PdfImage(pdfimageobj)
                # pdfimage is a pikepdf.PdfImage wrapper
                pil = pdfimage.as_pil_image()  # Pillow Image

                # process with Pillow (resize / compress)
                pil_processed = compress_pil_image(pil)

                # get raw pixel bytes (RGB)
                raw = pil_processed.tobytes()

                # compress with zlib and write into the existing image stream
                rawimage = pdfimage.obj  # the underlying stream object
                compressed = zlib.compress(raw)

                # Write raw image data compressed with FlateDecode
                # NOTE: if you want JPEG streams instead, you'd set Filter=/DCTDecode and write JPEG bytes
                rawimage.write(compressed, filter=Name("/FlateDecode"))
                rawimage.ColorSpace = Name("/DeviceRGB")
                rawimage.Width = pil_processed.width
                rawimage.Height = pil_processed.height
                rawimage.BitsPerComponent = 8

                # If the image was used across many pages, this will replace every occurrence.
                # If you want to only replace a single occurrence, you'd need to dig deeper into XObjects usage.

        pdf.save(output_path, compress_streams=True)
