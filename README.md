# Wiltivation Auto-Post Bot

Generates on-brand quote carousels and posts them to Instagram on a schedule, fully automated.

## How it works
Every scheduled run: picks 3 unused quotes -> renders a 4-slide carousel (3 quotes + CTA) ->
commits the images to this repo -> publishes the carousel to @wiltivation via Instagram's Graph API.

## One-time setup (~30-45 min)

### 1. Make @wiltivation a Business/Creator account
Instagram app -> Settings -> Account type -> switch to Professional -> Creator (or Business).

### 2. Link it to a Facebook Page
Instagram Settings -> Sharing to Facebook -> connect (or create) a Facebook Page. This is
required by the Graph API even though you're only posting to Instagram.

### 3. Create a Meta developer app
- Go to developers.facebook.com -> My Apps -> Create App -> type "Business"
- Add the "Instagram Graph API" product to the app
- Under App Roles, make sure your own Meta account is an Admin/Developer on the app

### 4. Get your IG_USER_ID and a long-lived access token
- In Graph API Explorer (developers.facebook.com/tools/explorer), select your app,
  get a User Access Token with these permissions: `instagram_basic`,
  `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`
- Call `GET /me/accounts` to find your Facebook Page's ID and Page access token
- Call `GET /{page-id}?fields=instagram_business_account` to get your `IG_USER_ID`
- Exchange the short-lived token for a long-lived one (60 days) via
  `GET /oauth/access_token?grant_type=fb_exchange_token&client_id=...&client_secret=...&fb_exchange_token=...`
- Long-lived Page tokens don't expire as long as you refresh periodically -- set a
  calendar reminder ~50 days out to regenerate `IG_ACCESS_TOKEN`, or automate the
  refresh call later if this becomes annoying.

### 5. Create the GitHub repo
- Create a **public** repo (raw.githubusercontent.com only serves public repos for free)
  called something like `wiltivation-bot`
- Push all the files in this folder to it

### 6. Add your secrets
Repo -> Settings -> Secrets and variables -> Actions -> New repository secret:
- `IG_USER_ID` — from step 4
- `IG_ACCESS_TOKEN` — from step 4

### 7. Set your posting schedule
Edit `.github/workflows/post.yml` — the cron line controls when it runs (UTC time,
Mon/Wed/Fri by default). Cron doesn't handle daylight saving automatically, so
revisit the UTC offset twice a year.

### 8. Test it
Repo -> Actions tab -> "Wiltivation Auto-Post" -> Run workflow (manual trigger).
Check the run logs, then check @wiltivation.

## Files
- `quote_generator.py` — seed bank of 24 quotes (2-3 sentences, no repeats until cycled)
- `generate_carousel.py` — renders the quotes into on-brand slide images
- `post_to_instagram.py` — publishes the carousel via Graph API
- `pipeline.py` — orchestrates all three + commits images so they're publicly fetchable
- `.github/workflows/post.yml` — the schedule

## When the quote bank runs low
You'll cycle through all 24 quotes roughly every 8 weeks at 3x/week. Either:
- Add more quotes by hand to `SEED_BANK` in `quote_generator.py`, or
- Set `ANTHROPIC_API_KEY` as a repo secret and call `generate_more_via_claude()`
  to top up the bank automatically (not wired into the schedule yet -- ask if
  you want that added as its own monthly workflow)

## Adjusting the brand look
Colors, fonts, and layout are all in `generate_carousel.py` under `BRAND CONFIG`.
Current palette is a placeholder (charcoal / cream / gold) -- swap in your actual
Wiltivation hex codes whenever you're ready.
