import json
import os
import urllib.request
from pathlib import Path

QUERY = """query($login:String!) { user(login:$login) { contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { contributionCount date } } } } } }"""
LOGIN = "codebyjhade"
TOKEN = os.environ["GITHUB_TOKEN"]

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": "codebyjhade-profile"},
)
with urllib.request.urlopen(request) as response:
    payload = json.load(response)

if payload.get("errors"):
    raise RuntimeError(payload["errors"])

calendar = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
weeks = calendar["weeks"][-53:]
counts = [day["contributionCount"] for week in weeks for day in week["contributionDays"]]
maximum = max(counts, default=0)

def level(count):
    if count == 0 or maximum == 0:
        return 0
    ratio = count / maximum
    if ratio <= .2:
        return 1
    if ratio <= .45:
        return 2
    if ratio <= .7:
        return 3
    return 4

colors = ["#24242b", "#3b365f", "#554c91", "#7062cc", "#8b7cff"]
cells = []
for column, week in enumerate(weeks):
    for row, day in enumerate(week["contributionDays"]):
        x, y = 31 + column * 16, 61 + row * 16
        delay = (column + row) * .012
        cells.append(
            f'<rect x="{x}" y="{y}" width="11" height="11" rx="3" fill="{colors[level(day["contributionCount"])]}" '
            f'style="opacity:0;animation:cell .35s ease-out {delay:.3f}s forwards"><title>{day["date"]}: {day["contributionCount"]} contributions</title></rect>'
        )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="920" height="210" viewBox="0 0 920 210" role="img" aria-labelledby="title desc">
<title id="title">GitHub contribution activity</title><desc id="desc">{calendar["totalContributions"]} contributions in the last year.</desc>
<style>@keyframes cell{{from{{opacity:0;transform:translateY(5px)}}to{{opacity:1;transform:translateY(0)}}}}@media(prefers-reduced-motion:reduce){{rect{{animation:none!important;opacity:1!important}}}}</style>
<rect x="1" y="1" width="918" height="208" rx="16" fill="#101014" stroke="#34343d" stroke-width="2"/>
<text x="30" y="36" fill="#8b7cff" font-family="ui-monospace,monospace" font-size="13">ACTIVITY / LAST 12 MONTHS</text>
{''.join(cells)}
<text x="30" y="190" fill="#aaa8b2" font-family="ui-monospace,monospace" font-size="13">{calendar["totalContributions"]} CONTRIBUTIONS · CONSISTENCY OVER VANITY</text>
</svg>'''
Path("assets/contributions.svg").write_text(svg, encoding="utf-8")
