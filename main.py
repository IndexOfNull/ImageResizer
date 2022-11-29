import os
from os import path
from PIL import Image, ImageOps
from io import BytesIO
import logging
import argparse
from logging_formatter import CustomFormatter

parser = argparse.ArgumentParser(prog="Image Resizer", description="Cut down on file size!")
parser.add_argument('input', nargs='*')
parser.add_argument('-l', '--lazy', default=False, action='store_true', help="Stop querying sizes when a suitable one is found")
parser.add_argument('--iter', help="How many sizes to query for each image")
parser.add_argument('-v', '--verbose', action='count', default=0)
parser.add_argument('-s', '--size', default=0, type=float, help="Target size (in MB)")
parser.add_argument('-y', '--yes', action='store_true', help="Automatically bypass in-place warning.")

args = parser.parse_args()

if args.verbose > 0:
    level = logging.DEBUG
else:
    level = logging.INFO

logger = logging.getLogger("ImageResizer")
logger.setLevel(level)
logging_ch = logging.StreamHandler()
logging_ch.setLevel(logging.DEBUG)
logging_ch.setFormatter(CustomFormatter())
logger.addHandler(logging_ch)

try:
    if not args.input:
        args.input = [input("Enter the file/folder path to resize. (You can drag on drop the file/folder on the terminal window): ").strip('"')]

    if args.size == 0:
        args.size = float(input("Enter the maximum size to optimize images for (in megabytes): "))

    if not args.iter:
        user_in = input("How many iterations for each image? Larger values will produce images closer to the desired size, but will take longer [default=5]: ")
        if user_in == '':
            args.iter = 5
        else:
            args.iter = int(user_in)
    else:
        args.iter = int(args.iter)

except ValueError:
    logger.error("Input validation error")
    exit()

IMAGE_EXTENSIONS = ("png", "jpeg", "jpg")
MAX_SIZE_BYTES = args.size * 1000 * 1000
get_extension = lambda pth: path.splitext(pth)[1][1:] # Get file extension and cut off preceding period

# Begin the real program!

paths = []

for input_directory in args.input:
    if not path.exists(input_directory):
        logger.error(f"{input_directory} does not exist")
        exit()
    elif path.isfile(input_directory):
        paths.append(input_directory)
    else:
        for (root, dirs, files) in os.walk(input_directory, topdown=True):
            for file in files:
                paths.append(path.join(root, file))

image_paths = list(filter(lambda x: get_extension(x) in IMAGE_EXTENSIONS, paths))
rescale_needed = list(filter(lambda x: path.getsize(x) > MAX_SIZE_BYTES, image_paths))

if not args.yes:
    response = input("Warning! This will modify files in-place. Be sure to make a backup before running! Continue [y/N]? ")
    if response.lower() not in ("y", "yes"):
        logger.info("Exiting...")
        exit()

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

# Returns BytesIO object with resized image. Returns None if no possible scale found. Returns False if input size is already under the limit
def resize_image(pth, *, it=6, max_size=MAX_SIZE_BYTES, lazy=False):
    original_size = path.getsize(pth)
    if original_size <= max_size:
        return False

    scale_factor = 0.5
    step_size = 0.5 # Will be divided by 2 then added/subtracted to scale factor
    img = Image.open(pth)
    img_format = img.format
    img = ImageOps.exif_transpose(img)
    best_resized = None

    logger.debug(f"Processing {pth}")

    for i in range(it):
        new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
        resized = img.resize(new_size)

        resized_bio = BytesIO()
        resized.save(resized_bio, img_format)
        resized_size = resized_bio.getbuffer().nbytes
        
        logger.debug(f"+ Testing size {new_size}. Result: {sizeof_fmt(resized_size)}")

        step_size /= 2
        if resized_size > max_size: # Still too big
            scale_factor -= step_size
        elif not lazy: # Resized size is smaller than max and we're not on lazy mode
            scale_factor += step_size
            best_resized = resized_bio
        else:
            break
    return best_resized

logger.info("--- Processing Images ---")
for img in rescale_needed:
    resized = resize_image(img, it=args.iter, max_size=MAX_SIZE_BYTES)
    if resized is None or resized is False:
        logger.warning(f"{img} could not be resized")
        continue
    buffer = resized.getbuffer()
    logger.info(f"Resized {img} to {sizeof_fmt(buffer.nbytes)}")
    with open(img, "wb") as f:
        f.write(buffer)

logger.info(" ------------------------- ")

logger.info(f"Finished processing {len(image_paths)} images. Resized {len(rescale_needed)} images.")

if not args.yes:
    input("Press enter to exit...")