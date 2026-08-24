#!/usr/bin/env python3
import argparse
import html
import json
from datetime import date
from pathlib import Path


DEFAULT_PROJECT = {
    "description": "프로젝트 폴더",
    "status": "DEV",
    "links": [],
}


def build_projects(root, config):
    configured = {item["folder"]: item for item in config.get("projects", [])}
    ignored = set(config.get("ignored", []))
    folders = {
        path.name
        for path in root.iterdir()
        if path.is_dir() and not path.name.startswith(".") and path.name not in ignored
    }
    folders.update(configured)

    projects = []
    for folder in sorted(folders, key=lambda value: value.casefold()):
        project = {**DEFAULT_PROJECT, "folder": folder, "name": folder}
        project.update(configured.get(folder, {}))
        projects.append(project)
    return projects


def render_links(links):
    if not links:
        return '<span class="no-link">로컬 프로젝트</span>'
    output = []
    for link in links:
        css_class = "button primary" if link.get("primary") else "button"
        output.append(
            f'<a class="{css_class}" href="{html.escape(link["url"], quote=True)}" '
            f'target="_blank" rel="noopener">{html.escape(link["label"])}</a>'
        )
    return "".join(output)


def render_page(config, projects, updated):
    cards = []
    for project in projects:
        status = project.get("status", "DEV")
        cards.append(f'''<article class="card">
  <div class="card-head"><span class="initial">{html.escape(project["name"][:1].upper())}</span>
    <h2>{html.escape(project["name"])}</h2><span class="status {status.lower()}">{html.escape(status)}</span></div>
  <p class="description">{html.escape(project["description"])}</p>
  <p class="path">~/Desktop/projects/{html.escape(project["folder"])}</p>
  <div class="links">{render_links(project.get("links", []))}</div>
</article>''')

    title = html.escape(config.get("title", "작업 중인 프로젝트"))
    owner = html.escape(config.get("owner", "Mac"))
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="프로젝트">
<title>{title}</title>
<style>
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #101112; color: #eceff1; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
main {{ width: min(1080px, 100%); margin: auto; padding: max(28px, env(safe-area-inset-top)) 20px max(40px, env(safe-area-inset-bottom)); }}
header {{ display: flex; justify-content: space-between; align-items: end; gap: 16px; margin-bottom: 22px; }}
h1 {{ margin: 0; font-size: 24px; letter-spacing: 0; }}
.updated {{ margin: 0; color: #8c959d; font-size: 12px; white-space: nowrap; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 290px), 1fr)); gap: 12px; }}
.card {{ min-width: 0; padding: 18px; background: #191b1d; border: 1px solid #2b2f33; border-radius: 8px; }}
.card-head {{ display: flex; align-items: center; gap: 9px; min-width: 0; }}
.initial {{ display: grid; place-items: center; width: 28px; height: 28px; flex: 0 0 28px; border-radius: 6px; background: #263b40; color: #67d4df; font-size: 12px; font-weight: 800; }}
h2 {{ min-width: 0; margin: 0; overflow-wrap: anywhere; font-size: 16px; letter-spacing: 0; }}
.status {{ margin-left: auto; padding: 3px 7px; border-radius: 4px; color: #79dba5; background: #173326; font-size: 9px; font-weight: 800; }}
.status.dev {{ color: #8fc8ff; background: #172a3b; }}
.description {{ min-height: 38px; margin: 14px 0 10px; color: #b9c0c5; font-size: 13px; line-height: 1.45; }}
.path {{ margin: 0 0 14px; color: #6f7880; font-family: ui-monospace, monospace; font-size: 10px; overflow-wrap: anywhere; }}
.links {{ display: flex; flex-wrap: wrap; gap: 7px; min-height: 30px; align-items: center; }}
.button {{ padding: 7px 11px; border: 1px solid #3a4045; border-radius: 6px; color: #cbd1d5; text-decoration: none; font-size: 12px; font-weight: 650; }}
.button.primary {{ border-color: #2abccc; background: #2abccc; color: #071619; }}
.no-link {{ color: #69727a; font-size: 11px; }}
footer {{ margin-top: 24px; color: #646d74; text-align: center; font-size: 11px; }}
@media (max-width: 520px) {{ main {{ padding-left: 14px; padding-right: 14px; }} header {{ align-items: flex-start; flex-direction: column; gap: 5px; }} .description {{ min-height: 0; }} }}
</style>
</head>
<body><main>
<header><h1>{title}</h1><p class="updated">{updated} 업데이트</p></header>
<section class="grid">{"".join(cards)}</section>
<footer>{owner} · 자동 생성</footer>
</main></body>
</html>
'''


def main():
    parser = argparse.ArgumentParser(description="프로젝트 대시보드를 생성합니다.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("projects.json"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("projects.html"))
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    projects = build_projects(args.root, config)
    args.output.write_text(render_page(config, projects, date.today().isoformat()), encoding="utf-8")
    print(f"{len(projects)}개 프로젝트를 {args.output}에 반영했습니다.")


if __name__ == "__main__":
    main()
