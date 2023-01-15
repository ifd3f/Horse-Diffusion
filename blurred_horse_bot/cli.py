import os
import tempfile

import click
import flickr_api
from mastodon import Mastodon
from PIL import Image, ImageFilter

from .util import *

MAX_PHOTO_DIM = 600


@click.command()
@click.option(
    "--show",
    is_flag=True,
    help="Display the image after all processing. Useful for debugging.",
)
def cli(show):
    """
    "Totally Stable Diffusion" is an advanced AI that posts diffused images from stables.
    """

    mastodon = init_apis()

    photo = get_random_photo()

    im_path = tempfile.mktemp(suffix=".jpg")
    print(f"Saving to {im_path}")
    photo.save(im_path)

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

    post(mastodon, im_path, photo)

    print(f"Deleting {im_path}")
    os.remove(im_path)


def init_apis():
    """Initialize APIs."""

    flickr_api.set_keys(
        api_key=os.environ["FLICKR_API"],
        api_secret=os.environ["FLICKR_SECRET"],
    )

    print("Logging into Mastodon")
    mastodon = Mastodon(client_id=os.environ["MASTODON_APPDATA"])
    mastodon.log_in(
        username=os.environ["MASTODON_EMAIL"],
        password=os.environ["MASTODON_PASSWORD"],
        scopes=["read", "write"],
        to_file="pytooter_usercred.secret",
    )
    return mastodon
