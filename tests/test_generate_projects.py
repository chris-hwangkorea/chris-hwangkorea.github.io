import json
import tempfile
import unittest
from pathlib import Path

from generate_projects import build_projects, render_page


class GenerateProjectsTest(unittest.TestCase):
    def test_adds_unconfigured_project_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "known").mkdir()
            (root / "new-project").mkdir()
            config = {
                "ignored": ["dashboard"],
                "projects": [{"folder": "known", "name": "Known", "description": "Configured"}],
            }

            projects = build_projects(root, config)

            self.assertEqual([project["folder"] for project in projects], ["known", "new-project"])
            self.assertEqual(projects[1]["name"], "new-project")
            self.assertEqual(projects[1]["status"], "DEV")

    def test_ignores_hidden_and_configured_ignored_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for name in (".hidden", "dashboard", "visible"):
                (root / name).mkdir()

            projects = build_projects(root, {"ignored": ["dashboard"], "projects": []})

            self.assertEqual([project["folder"] for project in projects], ["visible"])

    def test_renders_configured_links_and_current_date(self):
        config = {
            "title": "작업 중인 프로젝트",
            "owner": "Chris",
            "projects": [],
        }
        projects = [{
            "folder": "sample",
            "name": "Sample",
            "description": "Example app",
            "status": "LIVE",
            "links": [{"label": "열기", "url": "https://example.com", "primary": True}],
        }]

        html = render_page(config, projects, "2026-08-25")

        self.assertIn("2026-08-25", html)
        self.assertIn('href="https://example.com"', html)
        self.assertIn("Example app", html)

    def test_renders_separate_link_groups(self):
        config = {"projects": []}
        projects = [{
            "folder": "gallery",
            "name": "Gallery",
            "description": "Themes",
            "status": "LIVE",
            "links": [],
            "linkGroups": [
                {"label": "테마", "links": [{"label": "오리지널", "url": "https://example.com/"}]},
                {"label": "관리자 도구", "links": [{"label": "업로드", "url": "https://example.com/admin"}]},
            ],
        }]

        page = render_page(config, projects, "2026-08-27")

        self.assertIn('<h3>테마</h3>', page)
        self.assertIn('<h3>관리자 도구</h3>', page)
        self.assertIn('>오리지널</a>', page)
        self.assertIn('>업로드</a>', page)
        self.assertNotIn("로컬 프로젝트", page)

    def test_does_not_duplicate_group_url_as_primary_link(self):
        config = {"projects": []}
        projects = [{
            "folder": "gallery",
            "name": "Gallery",
            "description": "Themes",
            "status": "LIVE",
            "links": [],
            "linkGroups": [{
                "label": "테마",
                "links": [{"label": "오리지널", "url": "https://example.com/"}],
            }],
        }]

        page = render_page(config, projects, "2026-08-27")

        self.assertEqual(page.count('href="https://example.com/"'), 1)


if __name__ == "__main__":
    unittest.main()
