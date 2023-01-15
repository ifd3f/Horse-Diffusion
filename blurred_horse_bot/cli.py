import os
import click
import flickr_api as flickr
from PIL import Image, ImageFilter
import tempfile
import random


MAX_PHOTO_DIM = 600


@click.command()
@click.option(
    "--show",
    is_flag=True,
    help="Display the image after all processing. Useful for debugging.",
)
def cli(show):
    flickr.set_keys(
        api_key=os.environ["FLICKR_API"],
        api_secret=os.environ["FLICKR_SECRET"],
    )

    horse_photo = random.choice(flickr.Photo.search(tags=["horse"]))
    print(f"Found image {horse_photo}")

    im_path = tempfile.mktemp(suffix=".jpg")
    print(f"Saving to {im_path}")
    horse_photo.save(im_path)

    im = Image.open(im_path)
    w, h = im.size

    newsize = None
    if w >= h and w > MAX_PHOTO_DIM: 
        newsize = (MAX_PHOTO_DIM, int(h * MAX_PHOTO_DIM / w))
    elif h >= w and h > MAX_PHOTO_DIM:
        newsize = (int(w * MAX_PHOTO_DIM / h), MAX_PHOTO_DIM)

    if newsize is not None:
        print(f"Resizing from {im.size} to {newsize}")
        im = im.resize(newsize)

    blur_radius = max(*im.size) * 0.02
    print(f"Blurring with radius {blur_radius}")
    im = im.filter(ImageFilter.BoxBlur(blur_radius))
    im.save(im_path, quality=50)
    im.close()

    if show:
        with Image.open(im_path) as im:
            im.show()

    print(f"Deleting {im_path}")
    os.remove(im_path)
