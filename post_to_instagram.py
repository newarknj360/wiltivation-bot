"""
Posts a generated carousel to Instagram via the Graph API.
Requires: Instagram BUSINESS/CREATOR account linked to a Facebook Page,
a Meta developer App, and a long-lived Page access token with
instagram_content_publish permission.

Setup once at developers.facebook.com -> create App -> add "Instagram Graph API"
product -> generate long-lived token for the Page connected to @wiltivation.
"""
import requests, time, os

GRAPH = "https://graph.facebook.com/v19.0"
IG_USER_ID = os.environ["IG_USER_ID"]          # your IG business account id
ACCESS_TOKEN = os.environ["IG_ACCESS_TOKEN"]   # long-lived page token

def _check(r, step):
    """raise_for_status but print Graph API's actual JSON error body first --
    the default requests error message hides exactly the part that says why."""
    if not r.ok:
        print(f"Graph API error during {step}: HTTP {r.status_code}")
        try:
            print(r.json())
        except ValueError:
            print(r.text)
    r.raise_for_status()

def upload_image_get_container(image_url, is_carousel_item=True):
    r = requests.post(f"{GRAPH}/{IG_USER_ID}/media", data={
        "image_url": image_url,
        "is_carousel_item": is_carousel_item,
        "access_token": ACCESS_TOKEN,
    })
    _check(r, "child container upload")
    return r.json()["id"]

def publish_carousel(image_urls, caption):
    # 1. upload each slide as a child container
    child_ids = [upload_image_get_container(u) for u in image_urls]

    # 2. create the parent carousel container
    r = requests.post(f"{GRAPH}/{IG_USER_ID}/media", data={
        "media_type": "CAROUSEL",
        "children": ",".join(child_ids),
        "caption": caption,
        "access_token": ACCESS_TOKEN,
    })
    _check(r, "carousel container creation")
    creation_id = r.json()["id"]

    # 3. publish it
    time.sleep(3)  # let containers finish processing
    r = requests.post(f"{GRAPH}/{IG_USER_ID}/media_publish", data={
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN,
    })
    _check(r, "media_publish")
    return r.json()

if __name__ == "__main__":
    # NOTE: image_url must be a public HTTPS URL (Graph API can't take local files/base64).
    # In production, upload PNGs from generate_carousel.py to S3/Cloudflare R2/imgbb first,
    # then pass those public URLs here.
    urls = [
        "https://your-cdn.example.com/wiltivation_demo/post01_01.png",
        "https://your-cdn.example.com/wiltivation_demo/post01_02.png",
        "https://your-cdn.example.com/wiltivation_demo/post01_03.png",
        "https://your-cdn.example.com/wiltivation_demo/post01_04.png",
    ]
    caption = (
        "The man who needs no witnesses has already won.\n\n"
        "#solitude #discipline #stoicism #mindset #wiltivation"
    )
    print(publish_carousel(urls, caption))
