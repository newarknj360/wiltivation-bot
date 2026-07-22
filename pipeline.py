"""
Wiltivation full pipeline: quote -> carousel -> commit -> publish to Instagram.

Runs locally (python pipeline.py) or on schedule via
.github/workflows/post.yml. Requires this repo to be public (so
raw.githubusercontent.com URLs are fetchable by Instagram's Graph API)
or requires swapping the URL step for a real CDN if you want it private.
"""
import os, subprocess, datetime, json, time, requests

from quote_generator import get_batch
from generate_carousel import build_carousel
from post_to_instagram import publish_carousel

OUT_DIR = "posts"

def git(*args):
    subprocess.run(["git", *args], check=True)

def commit_and_push(paths, message):
    git("config", "user.email", "bot@wiltivation.local")
    git("config", "user.name", "wiltivation-bot")
    git("add", OUT_DIR, "state")
    # nothing to commit is not an error worth crashing on
    result = subprocess.run(["git", "commit", "-m", message])
    if result.returncode == 0:
        git("push")

def wait_until_public(urls, timeout=90):
    """Poll each raw.githubusercontent.com URL until it 200s, so Instagram
    doesn't try to fetch an image before GitHub's CDN has it."""
    deadline = time.time() + timeout
    for url in urls:
        while time.time() < deadline:
            r = requests.head(url)
            if r.status_code == 200:
                break
            time.sleep(3)
        else:
            raise TimeoutError(f"{url} never became reachable in {timeout}s")

def build_caption(slides, tag):
    tag_hashtags = {
        "solitude":   "#solitude #alonetime #innerwork #stillness",
        "discipline": "#discipline #disciplineequalsfreedom #consistency",
        "rebuilding": "#rebuild #comeback #startover #newchapter",
        "stoic":      "#stoicism #stoic #selfmastery #mindset",
        "resilience": "#resilience #mentaltoughness #growth",
    }
    base = "#motivation #selfimprovement #mindset #wiltivation"
    extra = tag_hashtags.get(tag, "")
    return f"{slides[0]}\n\n{base} {extra}".strip()

def run():
    repo = os.environ["GITHUB_REPOSITORY"]        # e.g. "willusername/wiltivation-bot"
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    today = datetime.date.today().isoformat()
    slug = today

    batch = get_batch(n=3)
    slides = [q["text"] for q in batch]
    tag = batch[0]["tag"]

    paths = build_carousel(slides, tag=tag, out_dir=OUT_DIR, slug=slug)
    commit_and_push(paths, f"content: {slug}")

    urls = [f"https://raw.githubusercontent.com/{repo}/{branch}/{p}" for p in paths]
    wait_until_public(urls)

    caption = build_caption(slides, tag)
    result = publish_carousel(urls, caption)
    print(json.dumps({"quotes": slides, "tag": tag, "urls": urls, "result": result}, indent=2))

if __name__ == "__main__":
    run()
