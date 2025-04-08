#!/usr/bin/python
# crop image area with cv2
# @github.com/motebaya - 7/10/2024

import cv2
import os
import logging
logging.basicConfig(level=logging.INFO)
from argparse import ArgumentParser, RawTextHelpFormatter
from colorama.ansi import Fore
import numpy as np

ext_list = [
  '.bmp', '.dib', '.jpeg', '.jpg', '.jpe',
  '.jp2', '.png', '.webp', '.pbm', '.pgm',
  '.ppm', '.sr', '.ras', '.tiff', '.tif',
  '.exr', '.hdr', '.pic'
]

def crop_img(
  img: str, x: int | float, y: int | float, w: int | float, h: int | float, margin: float = 0.5
  ) -> None:
  im = cv2.imdecode(np.fromfile(img, np.uint8), cv2.IMREAD_COLOR)
  width, height = im.shape[1], im.shape[0]
  x1 = int((x - w / 2) * width)
  y1 = int((y - h / 2) * height)
  x2 = int((x + w / 2) * width)
  y2 = int((y + h / 2) * height)
  margin_w, margin_h = int(margin * (x2 - x1)), int(margin * (y2 - y1)) # margin extend default 50%, from yolo it's too small!
  
  croped_outp = os.path.join(os.path.dirname(img), "cropped")
  if not os.path.exists(croped_outp):
    os.makedirs(croped_outp, exist_ok=True)

  outp = f"{croped_outp}/crop_{os.path.basename(img)}"
  fname, ext = os.path.splitext(outp)
  if os.path.exists(outp):
    outp = f"{fname}_1{ext}"

  # cv2 cannot read unicode filename
  is_ok, buffer = cv2.imencode(
    ext,
    im[max(y1 - margin_h, 0):min(y2 + margin_h, height), max(x1 - margin_w, 0):min(x2 + margin_w, width)]
  )
  if is_ok:
    buffer.tofile(outp)
    logging.info(f"Image cropped and saved to {outp}")
    return
  logging.error(f"{Fore.RED}Error cropping image: {img}")
  return

def bulk_crop(
  orig_target: str, 
  ratio_target: str,
  margin: float = 0.5
) -> None:
  """Bulk crop images based on ratio files.

  :param orig_target: Path to the directory containing the original images.
  :type orig_target: str
  :param ratio_target: Path to the directory containing the ratio files. 
    Each ratio file should have cropping coordinates for the corresponding image.
  :type ratio_target: str
  
  :example
     python detect.py --source inference/images --weights weights/yolov5x_anime.pt --output inference/output --save-txt
     
  """
  if os.path.isdir(orig_target) and os.path.isdir(ratio_target):
    img_list = os.listdir(orig_target)
    for i, img in enumerate(img_list, 1):
      img_name, ext = os.path.splitext(img)
      if ext.lower() not in ext_list:
        logging.warning(f"{Fore.YELLOW}Unsupported file type: {img_name}{ext}{Fore.RESET}")
        continue
      
      ratio = os.path.join(ratio_target, f"{img_name}.txt")
      if not os.path.exists(ratio):
        logging.warning(f"{Fore.YELLOW}Ratio file not found: {ratio}{Fore.RESET}")
        continue
      
      ratio_list = open(ratio, 'r').read().strip().splitlines()
      for ix, rt in enumerate(ratio_list, 1):
        x, y, w, h = rt.strip().split()[1:]
        logging.info(
          f" * Cropping:{ix} of {len(ratio_list)} RATIO - {i} of {len(img_list)} IMAGES - {img_name} - {x}, {y}, {w}, {h}"
        )
        try:
          crop_img(
            os.path.join(orig_target, img),
            float(x), float(y), float(w), float(h),
            margin=margin
          )
        except Exception as e:
          logging.error(f"{Fore.RED}Error cropping {img_name}: {e}{Fore.RESET}")
          continue
  else:
    logging.error(f"{Fore.RED}Invalid directories provided.{Fore.RESET}")
    return

# bulk_crop(
#   "./inference/images",
#   "./inference/output"
# )

# crop_img(
#   "./inference/images/mell.jpg",
#   0.60925, 0.26052, 0.263955, 0.178198,
#   margin=0.5
# )

if __name__=="__main__":
  parser = ArgumentParser(
    description="Crop images based on coordinates.",
    formatter_class=RawTextHelpFormatter
  )
  parser.add_argument(
    '-i', '--input', type=str, help="Path to the input images.", metavar=""
  )
  parser.add_argument(
    "-r", "--ratio", type=str, help="Path to the ratio files.", metavar=""
  )
  parser.add_argument(
    "-m", "--margin", type=float, default=0.5, help="Optional Extend Margin for cropping.", metavar=""
  )
  args = parser.parse_args()
  if not args.input or not args.ratio:
    parser.print_help()
    exit(1)
  
  bulk_crop(
    args.input,
    args.ratio,
    args.margin or 0.5
  )
        
# im0 = cv2.imread('./inference/images/mell.jpg')
# img_width, img_height = im0.shape[1], im0.shape[0]  # Ukuran gambar
# x_center, y_center, w, h = 0.60925, 0.26052, 0.263955, 0.178198 

# x1 = int((x_center - w / 2) * img_width)
# y1 = int((y_center - h / 2) * img_height)
# x2 = int((x_center + w / 2) * img_width)
# y2 = int((y_center + h / 2) * img_height)
# xyxy = (x1, y1, x2, y2)

# margin_w = int(0.5 * (x2 - x1)) # 20%
# margin_h = int(0.5 * (y2 - y1)) # 20%

# x1 = max(x1 - margin_w, 0)
# y1 = max(y1 - margin_h, 0)
# x2 = min(x2 + margin_w, img_width)
# y2 = min(y2 + margin_h, img_height)
# cropped_img = im0[y1:y2, x1:x2]
# cv2.imwrite("cropped1.jpg", cropped_img)

# cropped_img = im0[int(xyxy[1]):int(xyxy[3]), int(xyxy[0]):int(xyxy[2])]

# plot_one_box(xyxy, im0, label='croped', color=108, line_thickness=3)