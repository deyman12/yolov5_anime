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
from io import BytesIO
import logging
import re
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

def set_resize(
  image:str, 
  quality: int = 95, 
  minsize: int = 0
) -> None:
  """PNG format is to large

  :param str image: image path
  :param int quality: image quality, defaults to 90
  """
  outp = os.path.join(
    os.path.dirname(image),
    'resized'
  )
  if not os.path.exists(outp):
    os.makedirs(outp, exist_ok=True)
  
  if minsize:
    if os.path.getsize(image) <= minsize:
      logging.info(f"{Fore.YELLOW}Image is already smaller than {minsize} bytes: {image}{Fore.RESET}")
      shutil.copy(
        image, outp
      )
      logging.info(f"{Fore.GREEN}Image copied to {outp}{Fore.RESET}")
      return
    
    ratio = 0.9 # 10%
    at = 0
    buffer = BytesIO()
    while at < 5:
      buffer.seek(0)
      img = Image.open(image).convert("RGB")
      img.save(buffer, "JPEG", quality=quality)
      size_now = buffer.tell()
      
      if size_now <= minsize:
        buffer.seek(0)
        img = Image.open(buffer)
        outpfile = f"{outp}/resize-{os.path.splitext(os.path.basename(image))[0]}.jpg"
        img.save(
          outpfile,
          "JPEG",
          quality=quality
        )
        logging.info(f"Image resized and saved to {outpfile}")
        return
      
      w,h = img.size
      img =  img.resize(
        (int(w * ratio), int(h * ratio)),
      )
      quality = max(50, quality - 10) # reduce quality till 50% is not god idea
      at += 1
    
    buffer.seek(0)
    return Image.open(buffer)
  else:
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
    shutil.copy(
      image, outp
    )
    logging.info(f"{Fore.GREEN}Image copied to {outp}{Fore.RESET}")
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
  else:
    logging.warning(f"{Fore.YELLOW}Image path not found: {image}{Fore.RESET}")
  return

def parse_minsize(minsize: str) -> int:
  """parse minimum size

  :param str minsize: minimum size
  :raises ValueError: invalid minimum size
  :return int: minimum size in bytes
  """
  minsize = minsize.strip().upper()
  units = {
    "B": 1,
    "KB": 1024,
    "MB": 1024 ** 2,
    "GB": 1024 ** 3
  }
  m = re.match(r"^\s*([\d.]+)\s*(B|KB|MB|GB)\s*$", minsize.strip(), re.IGNORECASE)  
  if not m:
    raise ValueError(f"Invalid minimum size: {minsize}")
  
  v,u = m.groups()
  return int(float(v) * units[u.upper()])

def bulk_set(
  orig_target: str,
  execute: str = 'filter',
  minsize: str = '1MB'
) -> None:
  """bulk filter/resize images in directory

  :param str orig_target: targetr directory
  :return: None
  """
  if minsize: 
    minsize = parse_minsize(minsize)
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
          set_resize(
            f"{orig_target}/{image}",
            minsize=minsize
          )
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
    "-m", "--minsize", 
    type=str,
    help="Set minimum size to be resized, if <img_size> >= <minsize>,\nthen it will be resized until the size < <minsize>. e.g:[1KB, 1MB, 1GB]",
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
  
  bulk_set(args.directory, args.execute, args.minsize)

# bulk_filter(
#   "./AsumiSena/cropped"
# )
# set_resize("./sena.png")