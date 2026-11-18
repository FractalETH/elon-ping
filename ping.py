#!/usr/bin/env python3
"""One-shot: checks @elonmusk original posts/quotes (no RTs/replies) and pings a webhook. No AI usage."""
import os, json, re, urllib.request, datetime
UID = "44196397"; STATE = "since_id.txt"; MAX_AGE_MIN = 30
def get(url):
    r = urllib.request.Request(url, headers={"Authorization": "Bearer " + os.environ["X_BEARER_TOKEN"]})
    with urllib.request.urlopen(r, timeout=30) as resp: return json.load(resp)
def ping(p):
    body = json.dumps({"source": "elon-ping-gha", "post_id": p["id"], "url": f"https://x.com/elonmusk/status/{p['id']}",
        "created_at": p.get("created_at"), "text": p.get("text", ""),
        "quoted": any(t["type"] == "quoted" for t in p.get("referenced_tweets", []))}).encode()
    r = urllib.request.Request(os.environ["ELON_PING_WEBHOOK_URL"], data=body, method="POST",
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + os.environ["ELON_PING_WEBHOOK_KEY"]})
    with urllib.request.urlopen(r, timeout=30) as resp: return resp.status
def low_content(text):
    return len(re.findall(r"[A-Za-z0-9]", re.sub(r"https?://\S+|@\w+", "", text))) < 4
since = open(STATE).read().strip() if os.path.exists(STATE) else ""
url = f"https://api.x.com/2/users/{UID}/tweets?max_results=5&exclude=retweets,replies&tweet.fields=created_at,referenced_tweets"
if since: url += f"&since_id={since}"
posts = get(url).get("data", [])
now = datetime.datetime.now(datetime.timezone.utc)
for p in sorted(posts, key=lambda p: int(p["id"])):
    age = (now - datetime.datetime.fromisoformat(p["created_at"].replace("Z", "+00:00"))).total_seconds() / 60
    if age > MAX_AGE_MIN: print("skip old", p["id"]); continue
    if low_content(p.get("text", "")): print("skip low-content", p["id"]); continue
    print("ping", p["id"], ping(p))
if posts:
    open(STATE, "w").write(max(posts, key=lambda p: int(p["id"]))["id"])
