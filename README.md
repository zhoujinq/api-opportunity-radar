# AI API 商机雷达

一个可自定义的 Skill + 静态周报工作台：每周从公开信号中保留少量值得人工验证的商机卡，同时从 Agent 使用记录中复盘**用户本人**学会了什么，以及这项成长怎样改善商业产出。

> 当前是 MVP 0.1.0。公开页面使用演示快照：技术信号来自官方页面；商业假设不代表采购意向。成长条目来自用户提供的成长日志，已脱敏抽象，不公开原始聊天。

## 三秒理解

- 不是资讯聚合：每张卡都有公开来源、商业假设、待验证角色和下一动作。
- 不是 Agent 自夸：成长必须能定位到项目与对话，并写明结论边界。
- 不是自动销售机器：不自动触达，不生成成交概率，不虚构商业结果。

## 直接使用网页

直接打开根目录 `index.html`，或用任意静态服务器：

```bash
python -m http.server 8000
```

访问 `http://localhost:8000`。无需 npm install、构建或后端；字体和逻辑均随仓库提供。

网页支持：自定义名称/方向/周期、新增商机、新增成长、人工审核、localStorage 本地保存、Markdown 导出、恢复演示快照。

## 使用 Skill

Skill 位于 `skill/api-opportunity-radar/`。复制到支持 Skill 的 Agent 工作区后，按其中的 `SKILL.md` 执行。

也可以只使用确定性脚本：

```bash
python skill/api-opportunity-radar/scripts/radar.py init --root my-radar
# 编辑 my-radar/config.json、opportunities.json、growth.json
python skill/api-opportunity-radar/scripts/radar.py validate --root my-radar
python skill/api-opportunity-radar/scripts/radar.py report --root my-radar --output my-radar/weekly.md
python skill/api-opportunity-radar/scripts/radar.py site --root my-radar --output my-radar/site
```

`init` 不会覆盖已有工作区。`site` 会生成独立静态页面并复制字体。

## 开发方式

采用需求依赖矩阵 + TDD 切片，而非一次性瀑布交付：

1. `docs/requirements-matrix.md` 先锁定数据边界、依赖与 MVP 排除项。
2. `tests/` 先写失败测试，再实现核心逻辑与 Skill CLI。
3. 浏览器验收桌面与手机、离线资源、交互与导出，最后发布。

运行测试：

```bash
node --test tests/core.test.mjs
python -m unittest discover -s tests -p "test_*.py" -v
```

JavaScript 使用 Node 内置测试器；Python 只使用标准库。网页核心逻辑与界面放在同一个 HTML 中，通过独立 `script` 块进行纯函数测试。

完整实测记录与桌面/手机整页截图见 [验收记录](docs/validation.md)。

## 目录

```text
.
├── index.html                         # 成品单页网站
├── assets/fonts/                     # 本地字体与 OFL 许可
├── skill/api-opportunity-radar/
│   ├── SKILL.md                      # Agent 工作流
│   ├── references/schema.md          # 数据约定
│   ├── scripts/radar.py              # 初始化、校验、周报、站点导出
│   └── assets/
│       ├── workspace-template/       # 可自定义 JSON 工作区
│       ├── site-template.html        # 网站模板
│       └── fonts/                    # 导出站点所需字体
├── tests/                            # Node + Python 测试
└── docs/                             # 需求依赖矩阵与视觉计划
```

## 数据与隐私

- 公开信号与私人 Agent 使用记录分开处理。
- 公开工作区禁止 `rawTranscript` 字段；不要提交原始聊天、客户隐私、未公开金额或密钥。
- `scores` 只是证据整理分，不是成交概率。
- 本地修改仅存当前浏览器；公开分享导出的周报前要再次脱敏。

## 字体

正文使用 Noto Sans SC，数字、日期与短元信息使用 Maple Mono。对应许可位于 `assets/fonts/`。

## License

MIT，见 `LICENSE`。字体保留各自 SIL Open Font License。
