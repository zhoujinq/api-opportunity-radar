import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skill' / 'api-opportunity-radar' / 'scripts' / 'radar.py'
SPEC = importlib.util.spec_from_file_location('radar', SCRIPT)
radar = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(radar)


class RadarSkillTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = pathlib.Path(self.tmp.name) / 'workspace'
        radar.init_workspace(self.workspace)

    def tearDown(self):
        self.tmp.cleanup()

    def test_init_creates_customizable_workspace(self):
        config = json.loads((self.workspace / 'config.json').read_text(encoding='utf-8'))
        self.assertEqual(config['name'], 'AI 商机雷达')
        self.assertTrue((self.workspace / 'opportunities.json').exists())
        self.assertTrue((self.workspace / 'growth.json').exists())

    def test_validate_accepts_template_and_rejects_unsafe_data(self):
        self.assertEqual(radar.validate_workspace(self.workspace), [])
        growth_path = self.workspace / 'growth.json'
        growth = json.loads(growth_path.read_text(encoding='utf-8'))
        growth[0]['rawTranscript'] = 'private chat'
        growth_path.write_text(json.dumps(growth), encoding='utf-8')
        self.assertIn('growth[0].rawTranscript', radar.validate_workspace(self.workspace))

    def test_report_contains_both_loops_and_source(self):
        output = self.workspace / 'weekly.md'
        radar.write_report(self.workspace, output)
        text = output.read_text(encoding='utf-8')
        self.assertIn('## 商机卡', text)
        self.assertIn('## 人的成长', text)
        self.assertIn('https://github.com/n8n-io/n8n', text)
        self.assertIn('假设待人工验证', text)

    def test_static_site_export_is_self_contained_and_has_real_data(self):
        output = pathlib.Path(self.tmp.name) / 'site'
        radar.write_site(self.workspace, output)
        html = (output / 'index.html').read_text(encoding='utf-8')
        self.assertNotIn('__RADAR_DATA__', html)
        self.assertIn('AI 商机雷达', html)
        self.assertTrue((output / 'assets' / 'fonts' / 'maple-regular.woff2').exists())


if __name__ == '__main__':
    unittest.main()
