import random

import flickr_api
from mastodon import Mastodon


def get_random_photo():
    photo = random.choice(flickr_api.Photo.search(tags=["horse"]))
    print(f"Found image {photo}")
    return photo


def post(mastodon: Mastodon, im_path: str, photo_info: flickr_api.Photo):
    page_url = photo_info.getPageUrl()
    description = f"{photo_info.title} (source: {page_url})"
    print(f"Posting to Mastodon with description: {description}")

    media = mastodon.media_post(im_path, description=description)
    mastodon.status_post("", media_ids=media)
