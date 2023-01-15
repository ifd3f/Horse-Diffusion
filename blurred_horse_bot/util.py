import random

import flickr_api
from mastodon import Mastodon


def get_random_photo():
    search_results = flickr_api.Photo.search(
        tags=["horse"],
        per_page=500,
        page=random.randint(1, 50),
    )
    photo = random.choice(search_results)
    print(f"Found image {photo}")
    return photo


def post(mastodon: Mastodon, im_path: str, photo_info: flickr_api.Photo):
    page_url = photo_info.getPageUrl()
    description = f"{photo_info.title} (source: {page_url})"
    print(f"Posting to Mastodon with description: {description}")

    media = mastodon.media_post(im_path, description=description)
    mastodon.status_post("", media_ids=media)
