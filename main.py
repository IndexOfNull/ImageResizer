import os
from os import path
from PIL import Image
from io import BytesIO
import logging
import argparse

parser = argparse.ArgumentParser(prog="Image Resizer", description="Cut down on file size!")
parser.add_argument('input', nargs='*')
parser.add_argument('-l', '--lazy', default=False, action='store_true', help="Stop querying sizes when a suitable one is found")
parser.add_argument('--iter', default=5, help="How many sizes to query for each image")
parser.add_argument('-v', '--verbose', action='count', default=0)
parser.add_argument('-s', '--size', default=0, type=float, help="Target size (in MB)")
parser.add_argument('-y', '--yes', action='store_true', help="Automatically bypass in-place warning.")

args = parser.parse_args()
try:
    if not args.input:
        args.input = [input("Enter the file/folder path to resize. (You can drag on drop the file/folder on the terminal window): ").strip('"')]

    if args.size == 0:
        args.size = float(input("Enter the maximum size to optimize images for [megabytes]: "))
except ValueError:
    print("Input validation error")
    exit()

IMAGE_EXTENSIONS = ("png", "jpeg", "jpg")
MAX_SIZE_BYTES = args.size * 1000 * 1000
get_extension = lambda pth: path.splitext(pth)[1][1:] # Get file extension and cut off preceding period

PIL_FILE_TYPES = {
    "jpg": "jpeg",
    "jpeg": "jpeg",
    "png": "png",
}

if args.verbose > 0:
    level = logging.DEBUG
else:
    level = logging.INFO

logging.basicConfig(level=level, format="%(message)s")

# Begin the real program!

paths = []

for input_directory in args.input:
    if not path.exists(input_directory):
        print(f"{input_directory} does not exist")
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
        print("Exiting...")
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

    file_ext = get_extension(pth).lower()
    if not file_ext in PIL_FILE_TYPES:
        logging.error(f"{pth} does not have a supported file extention.")
        return False
    
    scale_factor = 0.5
    step_size = 0.5 # Will be divided by 2 then added/subtracted to scale factor
    img = Image.open(pth)
    best_resized = None

    logging.debug(f"Processing {pth}")

    for i in range(it):
        new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
        resized = img.resize(new_size)

        resized_bio = BytesIO()
        resized.save(resized_bio, file_ext)
        resized_size = resized_bio.getbuffer().nbytes
        
        logging.debug(f"+ Testing size {new_size}. Result: {sizeof_fmt(resized_size)}")

        step_size /= 2
        if resized_size > max_size: # Still too big
            scale_factor -= step_size
        elif not lazy: # Resized size is smaller than max and we're not on lazy mode
            scale_factor += step_size
            best_resized = resized_bio
        else:
            break
    return best_resized

logging.info("--- Processing Images ---")
for img in rescale_needed:
    resized = resize_image(img, it=args.iter, max_size=MAX_SIZE_BYTES)
    buffer = resized.getbuffer()
    logging.info(f"Resized {img} to {sizeof_fmt(buffer.nbytes)}")
    if resized is None or resized is False:
        logging.warning(f"{img} could not be resized")
        continue
    with open(img, "wb") as f:
        f.write(buffer)

logging.info("-------------------------")

logging.info(f"Finished processing {len(image_paths)} images. Resized {len(rescale_needed)} images.")

if not args.yes:
    input("Press enter to exit...")