#!/usr/bin/python
# bulk image filter with pilgram
# @github.com/motebaya - 2/24/2025

import os
import shutil
import pilgram
import subprocess
from PIL import Image
from colorama.ansi import Fore
from argparse import ArgumentParser, RawTextHelpFormatter

import logging
logging.basicConfig(level=logging.INFO)

def set_filter(image: str) -> None:
  """filters set
  :param str image: image path
  :return: None
  """
  img_outp = os.path.join(os.path.dirname(image), 'effects')
  if not os.path.exists(img_outp):
    os.makedirs(img_outp, exist_ok=True)
  
  im = Image.open(image)
  filter_out = f"{img_outp}/mayfair-{os.path.basename(image)}"
  pilgram.mayfair(im).save(filter_out)
  im = Image.open(filter_out)
  pilgram.css.saturate(im, 1.5).save(filter_out)
  logging.info(f"Image filtered and saved to {filter_out}")
  return

def set_resize(image:str, quality: int = 90) -> None:
  """PNG format is to large

  :param str image: image path
  :param int quality: image quality, defaults to 90
  """
  outp = os.path.join(
    os.path.dirname(image),
    'resized'
  )
  if image.endswith('.png'):
    img = Image.open(image).convert("RGB")
    if not os.path.exists(outp):
      os.makedirs(outp, exist_ok=True)
    
    img.save(
      os.path.join(
        outp,
        f"resize-{os.path.splitext(os.path.basename(image))[0]}.jpg"
      ),
      "JPEG",
      quality=quality
    )
    logging.info(f"Image converted and saved to {outp}")
    return
  logging.warning(f"{Fore.YELLOW}Image format not supported for conversion: {image}{Fore.RESET}")
  shutil.move(
    image, outp
  )
  logging.info(f"{Fore.GREEN}Image moved to {outp}{Fore.RESET}")
  return

def upscale(
  image: str,
  ESRGAN_PATH: str = r"realesrgan-ncnn-vulkan-20220424-windows/realesrgan-ncnn-vulkan.exe"
) -> None:
  if os.path.exists(image):
    outp = os.path.join(
      os.path.dirname(image),
      'upscaled'
    )
    if not os.path.exists(outp):
      os.makedirs(outp, exist_ok=True)
    args = [
      ESRGAN_PATH,
      "-i", str(image),
      "-o", str(outp),
      "-s", "4",
      "-n", "realesrgan-x4plus-anime",
      "-v"
    ]
    try:
      subprocess.run(args, check=True)
    except Exception as e:
      logging.error(f"{Fore.RED}Error upscaling image: {image} - {e}{Fore.RESET}")
      return
  logging.warning(f"{Fore.YELLOW}Image path not found: {image}{Fore.RESET}")
  return

def bulk_set(
  orig_target: str,
  execute: str = 'filter'
) -> None:
  """bulk filter/resize images in directory

  :param str orig_target: targetr directory
  :return: None
  """
  if os.path.isdir(orig_target):
    if execute == 'upscale':
      upscale(orig_target)
      return

    img_list = list(filter(
      lambda x: os.path.isfile(f"{orig_target}/{x}"), 
      os.listdir(orig_target)
    ))
    for i, image in enumerate(img_list, 1):
      try:
        logging.info(f"Processing [{execute}] image {i} of {len(img_list)}: {image}")
        if execute == 'resize':
          set_resize(f"{orig_target}/{image}")
        elif execute == 'filter':
          set_filter(
            f"{orig_target}/{image}"
          )
      except Exception as e:
        logging.error(f"{Fore.RED}Error filtering image: {image} - {e}{Fore.RESET}")
  return

if __name__ == "__main__":
  parser = ArgumentParser(
    description="Bulk image filter with pilgram\n   @github.com/motebaya",
    formatter_class=RawTextHelpFormatter
  )
  parser.add_argument(
    "-d", "--directory",
    type=str,
    help="Directory containing images to filter/resize",
    metavar=""
  )
  parser.add_argument(
    "-e", "--execute",
    type=str,
    default='filter',
    choices=['filter', 'resize', 'upscale'],
    help="Execute filter or resize",
    metavar=""
  )
  args = parser.parse_args()
  if not args.directory:
    parser.print_help()
    exit(1)
  
  bulk_set(args.directory, args.execute)

# bulk_filter(
#   "./AsumiSena/cropped"
# )
# set_resize("./sena.png")