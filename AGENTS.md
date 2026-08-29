# SysReptor 中文化改造指南（AGENTS.md）

> 本文档是 SysReptor 简体中文本地化（i18n）改造的总计划、规范与进度追踪文档。
> 任何 agent / 开发者参与本仓库的汉化工作前，必须先读完本文档。

## 一、项目目标

1. **中文操作界面**：前端（Nuxt 4 + Vuetify 4 SPA）全部用户可见文案提供简体中文翻译。
2. **zh-CN 语言支持**：后端 `Language` 枚举新增 `zh-CN`，支持创建中文项目 / 中文报告设计 / 中文查找模板。
3. **中文渗透测试模板**：
   - 完整中文化的报告设计（基于 Margherita）：`demo_data/demo-designs/margherita-zh-cn.toml`
   - 10 个官方演示查找模板追加 zh-CN 翻译（en-US 主翻译 + zh-CN 翻译块，双语可用）
   - 延伸：matrix 设计中文版、扩充常见中文漏洞模板
4. **本地部署**：Docker（colima）生产部署，导入中文模板，验证中文 PDF 渲染，还原个人使用的全部功能。

## 二、架构速览

| 目录 | 说明 |
|---|---|
| `api/` | Django 6 + DRF + Channels + Celery 后端（Poetry 管理，源码在 `api/src/sysreptor/`） |
| `packages/frontend/` | 主前端 Nuxt 4 SPA（`ssr:false`，静态生成后由 Django 托管），页面在 `src/pages/` |
| `packages/nuxt-base-layer/` | 共享 Nuxt layer：`S*` 基础组件、composables、Vuetify 配置 |
| `packages/rendering/` | PDF 渲染运行时（Vue bundle，Playwright/Chromium 执行后 WeasyPrint 出 PDF） |
| `packages/markdown/` | Markdown 编辑器（CodeMirror 6） |
| `packages/excalidraw/` | 内嵌绘图工具（React） |
| `packages/pdfviewer/` | PDF.js 查看器 |
| `plugins/` | 官方插件（iframe 方式加载，独立小 UI） |
| `demo_data/` | 报告设计 / 查找模板 / 演示项目（TOML 源），`reptor packarchive` 打包后经 `manage.py importdemodata` 或 REST 导入 |
| `deploy/` | 生产 docker-compose（db + redis + app） |
| `dev/` | 开发环境 docker-compose（热重载） |

**PDF 中文渲染**：官方镜像已内置 `fonts-noto-cjk`，fontconfig 自动回退，无需额外字体工作。

## 三、i18n 技术方案（重要约定）

**自研轻量 i18n 层，不用 vue-i18n。** 以英文原串为 key，未翻译自动回退英文，因此默认英文环境下测试（vitest/Playwright 断言英文文案）不受影响。

### 核心组件（均在 `packages/nuxt-base-layer/src/`）

- `composables/i18n.ts`：`useI18n()` → `{ t, locale }`；同时独立导出 `t(key, params)` 供 TS 模块使用。
  - `t('Username')` → 查词典，缺失返回 key 本身（英文原串）。
  - `t('Failed to load {name}', { name: 'x' })` → `{name}` 具名参数插值。
- `stores/locale.ts`：Pinia store（localStorage 持久化）。locale 检测顺序：localStorage → `navigator.language` 以 `zh` 开头则 `zh-CN` → 默认 `en`。切换时同步 `document.documentElement.lang` 与 Vuetify locale（`zhHans`）。
- `locales/zh-CN/*.json`：词典分片（按区域一文件），i18n composable 用 `import.meta.glob` 合并。**每个转换批次写自己的分片文件，避免冲突。**
- `components/S/LocaleSwitcher.vue`：语言切换器（简体中文 / English）。

### 转换规则（所有批量转换 agent 必须遵守）

> **模板用 `$t`，脚本用 `t`** —— `$t` 已通过 base layer 插件注册为全局属性（`packages/nuxt-base-layer/src/plugins/i18n.ts`），
> `t` 是 `packages/nuxt-base-layer/src/composables/i18n.ts` 的导出，经 Nuxt auto-import 直接可用（无需 import）。

1. 模板属性：`label="Username"` → `:label="$t('Username')"`；`title=`/`hint=`/`placeholder=`/`tooltip`/`messages`/`prepend-`/`append-`/`content` 同理。
2. 文本节点：`<span>Save</span>` → `<span>{{ $t('Save') }}</span>`。
3. `<script setup>` 内字符串（computed/computed 数组/函数返回值/toast）：直接调用 `t('Save')`（auto-import）。若文件内已有名为 `t` 的局部变量，改用 `const { t: translate } = useI18n()` 规避。
4. 插值：`` `Failed to load ${name}` `` → `t('Failed to load {name}', { name })`，词典里 `"Failed to load {name}": "加载 {name} 失败"`。
5. **禁译清单**：API 提交值、字段 id、enum 的 value（如 `retest_status` 的 `open`/`resolved`）、用户数据、代码示例、URL、CSS 类名、组件 prop 的非文案值、`data-testid`、路由 path。
6. 单复数：中文无复数，直接整句翻译；英文 key 保持原样（含复数形式）。
7. 词典 JSON：key/value 中的双引号转义 `\"`；换行用 `\n`。
8. 词典分片：写 `packages/nuxt-base-layer/src/locales/zh-CN/<区域>.json`（如 `auth.json`、`projects.json`、`notes.json`、`designer.json`、`settings.json`、`base.json`、`chat.json`）。跨区域通用词（Save/Cancel/Delete…）只写进 `common.json`，其它分片不要重复定义。同一 key 在多个分片出现时取合并后最后一个，务必保持译文一致。
9. 译文规范：安全行业通用术语（CVSS、OWASP、XSS、SQLi 等保留英文）；按钮用动词（保存/删除/取消/确认）；简洁专业。
10. date-fns 相对时间已由 `getDateFnsLocale()` 统一处理（Chip/Date、Chip/Expires、ShareDialog、项目删除提示、归档页已完成），其余调用点如遇再接入。
11. 转换后跑 `npm run --workspace=frontend test`（在 `packages/` 下）确认不破坏现有 vitest。
12. `SLocaleSwitcher`（语言切换器）已存在，需要的地方直接 `<s-locale-switcher />`。

### 后端约定

- `api/src/sysreptor/utils/language.py`：`CHINESE_SIMPLIFIED = 'zh-CN', False, 'Chinese Simplified (zh-CN)'`（无拼写检查支持，如实标注，同 Finnish 处理）。
- 后端 API 错误消息 / 邮件模板 / 服务端通知**保持英文**（已知限制，见第六节）。
- 部署时 `app.env` 设置 `PREFERRED_LANGUAGES=zh-CN,en-US,de-DE,...` 使中文在语言下拉中排最前。

## 四、任务进度

### Phase 0：仓库就位 + 本文档 ✅
- [x] 仓库克隆到 `/Users/dpdu/Desktop/opt/report_sysreptor/sysreptor`
- [x] 编写 AGENTS.md
- [x] 环境检查：Docker Desktop 已卸载 → 安装 colima + docker CLI；Node v23.11（可用）；Python 3.13

### Phase 1：i18n 基础设施 🔲
- [x] `composables/i18n.ts`（useI18n / t / getDateFnsLocale）
- [x] `stores/locale.ts`（持久化 + 检测 + Vuetify 同步）
- [x] `locales/zh-CN/` 词典目录 + import.meta.glob 合并
- [x] `components/S/LocaleSwitcher.vue` + 接入用户菜单
- [x] `vuetify.config.ts` 配置 `zhHans` locale
- [x] date-fns `formatDistanceToNow` 调用点接入 locale
- [x] `frontend/nuxt.config.ts` htmlAttrs.lang 动态化（app.vue 运行时同步）

### Phase 2：批量字符串转换 ✅
- [x] 2A 登录/认证/错误页 + 用户资料/MFA/API令牌/公钥/安全/通知设置（29 文件，auth.json 200 条）
- [x] 2B 项目列表/新建/详情 + findings/sections + 评论 + 历史版本（33 文件，projects.json 145 条）
- [x] 2C 笔记 + 分享 + Markdown 工具栏 + 图片编辑器（26 文件，notes.json 113 条）
- [x] 2D Designer 设计器 + 查找模板库（28 文件，designer.json 202 条）
- [x] 2E 管理/设置/备份/用户管理/license（5 文件，settings.json 56 条）
- [x] 2F nuxt-base-layer 全部 S* 组件 + composables（53 文件，base.json 214 条）
- [x] 2G AI Chat + utils 消息（9 文件，chat.json 47 条；rendering 包核查无硬编码文案跳过）
- [x] i18n 审计清零（`scripts/i18n-audit.py` 0 命中）；词典 key 覆盖校验通过（945 条）
- [x] 最终回归：vitest 12 文件 1002 测试全绿
- 已知词典冲突处理：`Active`（项目状态"进行中" vs CVSS"主动"）→ 项目导航改用 `Active Projects` key 隔离

## 部署（服务器 `us`）

> 本机不装 Docker（用户要求，已清理 colima/brew docker）。部署在 `ssh us` 服务器：
> Debian 12 x86_64 / 2C3.8G / Docker 29.7.2 / Compose v5.4 / root。镜像命名 `yingdao/<name>`（本地镜像，无私有 registry）。
> 同机上已有 weibo-plus 等业务容器，互不影响。已加 2G swap（/swapfile，fstab 持久化）防构建 OOM。

```bash
# 源码传输（服务器无 rsync，用 tar 管道；排除 node_modules/.git/.nuxt 等）
cd <repo> && tar czf - --exclude node_modules --exclude .git --exclude .nuxt \
  --exclude .playground --exclude test-reports --exclude dist --exclude .output . \
  | ssh us 'mkdir -p /opt/sysreptor && rm -rf /opt/sysreptor/* && tar xzf - -C /opt/sysreptor'

# 构建（约 30-60 分钟）
ssh us 'cd /opt/sysreptor && DOCKER_BUILDKIT=1 docker build -t yingdao/sysreptor:latest .'

# 部署（compose 文件 image 已改为 yingdao/sysreptor:${SYSREPTOR_VERSION:-latest}）
ssh us 'cd /opt/sysreptor/deploy && docker compose up -d'

# 超管 + 导入中文模板（tar 包从本机 /tmp 或重新 packarchive）
ssh us 'docker compose -f /opt/sysreptor/deploy/sysreptor/docker-compose.yml exec app \
  python3 manage.py createsuperuser ...'
```

### Phase 3：后端 zh-CN ✅
- [x] Language 枚举新增 zh-CN（`api/src/sysreptor/utils/language.py`）
- [x] 部署 `app.env` 设置 `PREFERRED_LANGUAGES=zh-CN,en-US,...` 使中文排最前

### Phase 4：中文渗透测试模板（进行中）
- [ ] `margherita-zh-cn.toml`（新 UUID，language=zh-CN，全量翻译 + assets 复制）【agent 进行中】
- [x] 10 个查找模板 TOML 追加 zh-CN 翻译块（sqli/stored_xss/csrf/xxe/http_security_headers/insecure_http_cookies/sensitive_data_in_url_parameters/session_management_weaknesses/untrusted_tls_certificates/user_enumeration）
- [x] `reptor packarchive` 验证：demo-templates 打包含 10 个 zh-CN 翻译
- [ ] 延伸：matrix-zh-cn + 常见中文漏洞模板扩充

### Phase 5：部署与验证 ✅（服务器 `us`）
- [x] 镜像构建 `yingdao/sysreptor:latest`（约 20 分钟，2 核 3.8G + 2G swap）
- [x] `docker volume create sysreptor-db-data / app-data`（compose external 卷）后 `docker compose up -d`
- [x] healthcheck 绿（database/migrations/cache = true）
- [x] 超管 `admin` 创建（密码见本地 `/tmp/sysreptor_admin_creds.txt`）
- [x] 导入数据：5 设计（含 2 个中文版）+ 15 模板（15 条 zh-CN 翻译，5 个中文主语言）
- [x] 端到端 API 冒烟：登录 → 创建中文项目（语言自动 zh-CN）→ fromtemplate 创建中文 finding → `POST /pentestprojects/{id}/generate/` 渲染 751KB PDF
- [x] PDF 中文验证：pdftotext 提取出完整中文（封面/目录/执行摘要/测试方法与范围/漏洞总览），CJK 字体正常
- [x] 前端 bundle 验证：中文词典（"简体中文"/"加载数据失败" 等）已打进 `_nuxt/*.js`；SPA 路由 200
- 访问方式：`ssh -L 8000:localhost:8000 us` 后浏览器开 http://localhost:8000（compose 默认绑 127.0.0.1:8000，未对公网暴露）

## 五、常用命令

```bash
# 前端依赖与测试（在 packages/ 目录）
npm ci
npm run --workspace=frontend test        # vitest
npm run --workspace=frontend dev         # 本地开发服务器（需 API 代理）

# 后端测试（在 api/src/ 目录，或 dev compose 内）
pytest

# 打包模板（demo_data 各子目录 → tar.gz）
pip install reptor
reptor packarchive demo_data/demo-designs -o demo-designs.tar.gz
reptor packarchive demo_data/demo-templates -o demo-templates.tar.gz

# 部署（在 deploy/ 目录）
docker compose build app
docker compose up -d
docker compose exec app python3 manage.py importdemodata --type=design < demo-designs.tar.gz
docker compose exec app python3 manage.py importdemodata --type=template < demo-templates.tar.gz

# colima（本机无 Docker Desktop）
colima start --cpu 4 --memory 8
```

## 六、已知限制（不做 / 延伸）

1. 后端 API 错误消息、服务端生成的通知标题/文本、邮件模板保持英文（个人使用影响小）。
2. Monaco 代码编辑器（Designer HTML/CSS 编辑器）界面为英文（Monaco 本地化需独立构建，性价比低）。
3. 插件 iframe UI（jira、cyberchef 等 14 个）保持英文，功能不受影响。
4. Excalidraw `langCode` 跟随 locale 为延伸项（其官方支持 zh-CN）。
5. zh-CN 无拼写检查（LanguageTool 不支持中文，如实标注）。

## 八、社区版备份功能（自实现）

官方"备份"为 PRO + BACKUP_KEY 双门槛。社区版自实现（复用 import/export 格式，未加密）：

- **导出**：`POST /api/v1/utils/export_all/`（admin/superuser）→ 全部设计 + 查找模板 + 项目打包为一个 .tar.gz（浏览器下载）
- **导入**：`POST /api/v1/utils/import_all/`（multipart file）→ 按 format 标记分组还原；**总是创建新副本**（新 UUID），不覆盖现有数据
- 前端：备份页新增"社区版数据备份"卡片（导出按钮 + 导入文件选择）
- 已知限制：备份未加密（个人使用可接受）；导入为复制语义而非覆盖
- 入口代码：`pentests/import_export/import_export.py`（export_all_archive / import_all_archive）+ `api_utils/views.py`（UtilsViewSet.export_all / import_all）

## 九、社区版 Version History（刚需，已解锁）

官方 Version History 依赖 Professional license。本 fork 社区版直接启用：

- `SIMPLE_HISTORY_ENABLED = True`（`conf/settings.py`，不再走 `LicenseCheckBooleanProxy`）
- `history_timeline` API 去掉 `license.is_professional()` 门禁（`pentests/views.py`）
- 前端 `history.vue` / `History/Timeline.vue` 去掉 Pro 升级 UI，始终加载时间线
- 自测：`GET /api/v1/pentestprojects/{id}/history-timeline/?mode=medium` → 200，有历史记录

**Concurrent Editing（评论 / 协作）仍为可选 TODO**：相关 view 仍挂 `ProfessionalLicenseRequired`，暂未解锁。

## 十、本机原生运行（无 Docker）

本机禁止安装 Docker；服务器 `us` 负责镜像。本机：

```bash
# API（Postgres/Redis 本地 + uvicorn :8001）
./api/run_local.sh

# 重建前端静态并拷到 Django 期望层级（避免黑屏）
./api/rebuild_frontend.sh
# 正确布局：api/src/frontend/index.html + api/src/frontend/static/_nuxt/...
# 切勿把 .output/public 整树嵌进 static/ 造成 static/static/_nuxt
```

浏览器：http://localhost:8001 （admin / 见本地凭证文件）

## 七、术语表（保证译文一致性）

| 英文 | 中文 |
|---|---|
| Project | 项目 |
| Finding | 发现（漏洞发现） |
| Section | 章节 |
| Note | 笔记 |
| Design / Report Design | 设计 / 报告设计 |
| Finding Template | 查找模板 |
| Designer | 设计器 |
| Render | 渲染 |
| Archive | 归档 |
| Review | 审核 |
| Comment | 评论 |
| Publish | 发布 |
| Executive Summary | 执行摘要 |
| Scope | 测试范围 |
| Methodology | 测试方法 |
| Vulnerability Overview | 漏洞总览 |
| Recommendation | 修复建议 |
| Impact | 影响 |
| References | 参考资料 |
| CVSS Severity (Critical/High/Medium/Low/Info) | 严重程度（严重/高危/中危/低危/提示） |
| Retest | 复测 |
| Pentester | 渗透测试工程师 |
