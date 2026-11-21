# 工作区数据约定

工作区包含三个 UTF-8 JSON 文件。字段缺失时先补数据，不要用自然语言报告掩盖结构问题。

## config.json

- `name`：雷达显示名，可完全自定义。
- `focus`：行业、客户类型或技术方向。
- `period`：本报告覆盖周期。
- `maxCards`：1—10，建议默认 5。

## opportunities.json

数组，每项字段：

- `id`：工作区内唯一、稳定的字符串。
- `name`：公开项目或组织名称。
- `source.label`：来源标题。
- `source.url`：可复核的 HTTPS URL。
- `signal`：来源能直接支持的公开事实。
- `hypothesis`：可证伪的商业假设，不写采购结论。
- `buyer`：待验证的角色，不虚构具体联系人。
- `nextAction`：一周内可执行的最小动作。
- `status`：`pending` / `follow` / `hold`。
- `archived`：可选；公开归档等反信号为 `true`。
- `scores`：可选；`signal/fit/timing/access` 各 0—5，仅用于整理证据，不是成交概率。

## growth.json

数组，每项字段：

- `id`：稳定字符串。
- `lesson`：用户本人学会或改变了什么。
- `project`：来源项目。
- `conversation`：日期时间 + 对话主题；公开版避免私密会话 ID。
- `evidence`：行为证据和不能推出的结论。
- `businessLink`：与商机发现、验证、交付或商业化的关系。
- `nextExperiment`：下一周可检验的动作。

公开工作区禁止 `rawTranscript`。私人原文、客户信息、密钥和未公开数字不得为了“证据充分”而写入公开仓库。
