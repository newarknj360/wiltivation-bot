"""
Wiltivation Quote Generator
Produces 2-3 sentence quotes (not one-liners) in the Wiltivation voice:
raw, direct, stoic-leaning, solitude/discipline/rebuilding themes.

Two modes:
1. Seed bank rotation (works offline, no API key needed) - default.
2. Live generation via Claude API (set ANTHROPIC_API_KEY) - tops up the
   bank automatically once you've cycled through the seeds.
"""
import json, os, random

STATE_FILE = os.path.join(os.path.dirname(__file__), "state", "used_quotes.json")

# ---------- SEED BANK: 24 quotes, 2-3 sentences each, tagged by theme ----------
SEED_BANK = [
    {"tag": "solitude", "text": "Nobody claps when you choose the harder path alone in a room with no witnesses. That silence is the price of building something real, and most people aren't willing to pay it."},
    {"tag": "solitude", "text": "You don't owe anyone an explanation for the version of yourself you're becoming. Keep building in the dark until the results speak louder than any excuse could."},
    {"tag": "discipline", "text": "Discipline doesn't feel like motivation. It feels like showing up on the days you'd rather disappear, and doing it anyway because you gave your word to no one but yourself."},
    {"tag": "discipline", "text": "The gap between who you are and who you could be is closed by boring, repeated decisions. Nobody is coming to make them for you."},
    {"tag": "rebuilding", "text": "Rock bottom isn't the end of your story, it's just the first honest chapter. Everything after this is a choice, not a sentence."},
    {"tag": "rebuilding", "text": "You don't rebuild in public. You rebuild in silence, alone with the version of yourself you're ashamed of, until you're not ashamed anymore."},
    {"tag": "solitude", "text": "The strongest men I've ever respected didn't perform their pain for an audience. They disappeared, did the work, and came back different, no announcement required."},
    {"tag": "stoic", "text": "You can't control what happened to you. You can control what you become because of it, and that's the only leverage that's ever mattered."},
    {"tag": "discipline", "text": "Motivation is a mood. Discipline is a decision you make before the mood ever shows up, which is why it's the only one you can trust."},
    {"tag": "solitude", "text": "Being alone isn't the punishment people think it is. It's the only place loud enough to hear who you actually are underneath everyone else's opinion of you."},
    {"tag": "resilience", "text": "Everything that broke you was also teaching you what you can survive. Stop calling it trauma and start calling it evidence."},
    {"tag": "stoic", "text": "The version of you that reacts to everything is not in control. The version of you that responds to almost nothing is the one people should fear."},
    {"tag": "discipline", "text": "You don't need a new plan. You need to do the plan you already have, on the day you don't feel like it, for longer than feels reasonable."},
    {"tag": "rebuilding", "text": "Starting over isn't weakness, it's the most honest thing a man can do. Pretending the old version still works is the actual failure."},
    {"tag": "solitude", "text": "Solitude builds what crowds destroy. Every skill worth having was earned in a room by yourself, long before anyone else knew your name."},
    {"tag": "stoic", "text": "Complaining is a tax you pay for staying the same. Silence and work are the only currency that's ever bought anyone a different life."},
    {"tag": "resilience", "text": "You were never behind. You were building on a timeline nobody else could see, and that's exactly why it's going to outlast theirs."},
    {"tag": "discipline", "text": "The people who make it aren't more talented, they're just harder to talk out of showing up. Consistency is a personality trait you build on purpose."},
    {"tag": "solitude", "text": "Withdraw for a season. Let people wonder where you went, and come back with something they can't argue with."},
    {"tag": "stoic", "text": "Control your reaction and you control the outcome, even when you can't control the event. That's not philosophy, that's the only real power you'll ever have."},
    {"tag": "rebuilding", "text": "The comeback always looks quiet from the outside. Inside, it's the loudest, most disciplined season of your entire life."},
    {"tag": "resilience", "text": "You don't need everyone to believe in the plan. You need to be stubborn enough to finish it while they're still deciding whether it'll work."},
    {"tag": "discipline", "text": "Talent gets you noticed. Discipline is what's left standing after everyone with more talent than you quit."},
    {"tag": "solitude", "text": "The right people won't need constant proof you're still working. The wrong people never will, no matter how much you show them."},
]

def _load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return set(json.load(f))
    return set()

def _save_state(used):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(list(used), f)

def get_batch(n=3, reset_if_exhausted=True):
    """Return n unused quotes, tracking what's already been posted so nothing repeats."""
    used = _load_state()
    available = [q for q in SEED_BANK if q["text"] not in used]
    if len(available) < n and reset_if_exhausted:
        used = set()
        available = SEED_BANK[:]
    batch = random.sample(available, min(n, len(available)))
    used.update(q["text"] for q in batch)
    _save_state(used)
    return batch

def generate_more_via_claude(n=8, existing_texts=None):
    """Optional: top up the bank with fresh quotes via the Claude API.
    Requires ANTHROPIC_API_KEY env var. Safe to skip if you'd rather just
    write more seeds by hand."""
    import requests
    existing_texts = existing_texts or [q["text"] for q in SEED_BANK]
    prompt = f"""Write {n} new quotes for a motivational Instagram page called Wiltivation.

Voice: raw, direct, stoic-leaning, faith-optional but not preachy. Themes: solitude,
discipline, rebuilding from rock bottom, silence over validation, self-respect.
Each quote must be exactly 2-3 sentences (never a one-liner, never longer than 3 sentences).
No em-dashes. No cliches like "the grind never stops" or "rise and grind".
Do not repeat or closely paraphrase any of these existing quotes:
{json.dumps(existing_texts, indent=2)}

Return ONLY a JSON array of objects like [{{"tag": "solitude", "text": "..."}}], nothing else."""

    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    r.raise_for_status()
    text = r.json()["content"][0]["text"]
    return json.loads(text.strip().strip("```json").strip("```"))

if __name__ == "__main__":
    batch = get_batch(n=3)
    print(json.dumps(batch, indent=2))
