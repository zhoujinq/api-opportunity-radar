"""Deterministic workspace, report and static-site tools for API Opportunity Radar."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = SKILL_DIR / 'assets' / 'workspace-template'
SITE_TEMPLATE = SKILL_DIR / 'assets' / 'site-template.html'
FONT_DIR = SKILL_DIR / 'assets' / 'fonts'
STATUS_LABELS = {'pending': '待人工审核', 'follow': '进入跟进', 'hold': '暂缓'}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def init_workspace(target: Path) -> None:
    target = Path(target)
    if target.exists():
        raise FileExistsError(f'Workspace already exists: {target}')
    shutil.copytree(TEMPLATE_DIR, target)


def load_workspace(root: Path) -> dict[str, Any]:
    root = Path(root)
    return {
        'config': read_json(root / 'config.json'),
        'opportunities': read_json(root / 'opportunities.json'),
        'growth': read_json(root / 'growth.json'),
    }


def validate_workspace(root: Path) -> list[str]:
    root = Path(root)
    errors: list[str] = []
    try:
        data = load_workspace(root)
    except (OSError, json.JSONDecodeError) as exc:
        return [f'workspace: {exc}']
    config = data['config']
    for key in ('name', 'focus', 'period'):
        if not str(config.get(key, '')).strip():
            errors.append(f'config.{key}')
    try:
        limit = int(config.get('maxCards', 0))
        if not 1 <= limit <= 10:
            errors.append('config.maxCards')
    except (TypeError, ValueError):
        errors.append('config.maxCards')
    if len(data['opportunities']) > int(config.get('maxCards', 10)):
        errors.append('opportunities.maxCards')
    for index, item in enumerate(data['opportunities']):
        for key in ('name', 'signal', 'hypothesis', 'buyer', 'nextAction'):
            if not str(item.get(key, '')).strip():
                errors.append(f'opportunities[{index}].{key}')
        url = str(item.get('source', {}).get('url', ''))
        if not url.startswith('https://') or ' ' in url:
            errors.append(f'opportunities[{index}].source.url')
        if item.get('status', 'pending') not in STATUS_LABELS:
            errors.append(f'opportunities[{index}].status')
    for index, item in enumerate(data['growth']):
        for key in ('lesson', 'project', 'conversation', 'evidence', 'businessLink', 'nextExperiment'):
            if not str(item.get(key, '')).strip():
                errors.append(f'growth[{index}].{key}')
        if 'rawTranscript' in item:
            errors.append(f'growth[{index}].rawTranscript')
    return errors


def build_report(data: dict[str, Any]) -> str:
    config = data['config']
    lines = [
        f"# {config['name']}", '',
        f"- 周期：{config['period']}",
        f"- 方向：{config['focus']}",
        '- 口径：公开信号为事实来源，商业假设待人工验证；不代表采购意向或实际成交。',
        '', '## 商机卡', '',
    ]
    for index, item in enumerate(data['opportunities'], 1):
        lines.extend([
            f"### {index}. {item['name']}", '',
            f"- 审核状态：{STATUS_LABELS.get(item.get('status', 'pending'), '待人工审核')}",
            f"- 公开信号：{item['signal']}",
            f"- 来源：[{item['source'].get('label', '公开来源')}]({item['source']['url']})",
            f"- 商业假设：{item['hypothesis']}",
            f"- 待验证买方：{item['buyer']}",
            f"- 下一动作：{item['nextAction']}", '',
        ])
    lines.extend(['## 人的成长', ''])
    for index, item in enumerate(data['growth'], 1):
        lines.extend([
            f"### {index}. {item['lesson']}", '',
            f"- 来源项目：{item['project']}",
            f"- 对话定位：{item['conversation']}",
            f"- 证据与边界：{item['evidence']}",
            f"- 商业关联：{item['businessLink']}",
            f"- 下一实验：{item['nextExperiment']}", '',
        ])
    lines.extend(['---', '由可自定义的商机雷达 Skill 生成；公开分享前请再次脱敏。'])
    return '\n'.join(lines)


def write_report(root: Path, output: Path) -> None:
    errors = validate_workspace(root)
    if errors:
        raise ValueError('Invalid workspace: ' + ', '.join(errors))
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_report(load_workspace(root)), encoding='utf-8')


def write_site(root: Path, output: Path) -> None:
    errors = validate_workspace(root)
    if errors:
        raise ValueError('Invalid workspace: ' + ', '.join(errors))
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    data = load_workspace(root)
    payload = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    template = SITE_TEMPLATE.read_text(encoding='utf-8')
    html, replacements = re.subn(r'const INITIAL_DATA = [\s\S]*?;\n', f'const INITIAL_DATA = {payload};\n', template, count=1)
    if replacements != 1:
        raise ValueError('Site template is missing the INITIAL_DATA block')
    (output / 'index.html').write_text(html, encoding='utf-8')
    shutil.copytree(FONT_DIR, output / 'assets' / 'fonts', dirs_exist_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Generate an evidence-led opportunity and human-growth weekly report.')
    commands = parser.add_subparsers(dest='command', required=True)
    init_parser = commands.add_parser('init', help='Create a new customizable workspace without overwriting files.')
    init_parser.add_argument('--root', type=Path, required=True)
    for name in ('validate', 'report', 'site'):
        sub = commands.add_parser(name)
        sub.add_argument('--root', type=Path, required=True)
        if name == 'report':
            sub.add_argument('--output', type=Path)
        if name == 'site':
            sub.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'init':
            init_workspace(args.root)
            print(f'Workspace created: {args.root}')
        elif args.command == 'validate':
            errors = validate_workspace(args.root)
            if errors:
                print('\n'.join(errors), file=sys.stderr)
                return 1
            print('Workspace valid.')
        elif args.command == 'report':
            output = args.output or args.root / 'weekly.md'
            write_report(args.root, output)
            print(f'Report written: {output}')
        elif args.command == 'site':
            write_site(args.root, args.output)
            print(f'Static site written: {args.output}')
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
