import json
import re
import urllib.request
from pathlib import Path

USER = "tiensang157"
START = "<!-- public-resource:start -->"
END = "<!-- public-resource:end -->"
README = Path("README.md")


def fetch():
    repos = []
    page = 1
    while True:
        url = (
            f"https://api.github.com/users/{USER}/repos"
            f"?per_page=100&type=owner&sort=updated&page={page}"
        )
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "tiensang157-profile",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as res:
            batch = json.load(res)
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def cell(text):
    text = (text or "").replace("\r", " ").replace("\n", " ").replace("|", "\\|").strip()
    return text or "—"


def table(repos):
    rows = ["| Tên | Mô tả | Ngôn ngữ |", "| --- | --- | --- |"]
    shown = [
        repo
        for repo in repos
        if not repo.get("fork") and not repo.get("private") and repo.get("name") != USER
    ]
    if not shown:
        rows.append("| — | Chưa có repo public. | — |")
    for repo in shown:
        rows.append(
            f"| [{cell(repo['name'])}]({repo['html_url']}) | {cell(repo.get('description'))} | {cell(repo.get('language'))} |"
        )
    return "\n".join([START, "", "## Public resource", "", *rows, "", END, ""])


def main():
    text = README.read_text(encoding="utf-8")
    block = table(fetch())
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.S)
    if pattern.search(text):
        text = pattern.sub(block, text, count=1)
    else:
        if not text.endswith("\n"):
            text += "\n"
        text = text.rstrip() + "\n\n" + block
    README.write_bytes(text.encode("utf-8"))


if __name__ == "__main__":
    main()
