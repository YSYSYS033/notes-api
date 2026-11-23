# notes-api

> FastAPI + SQLAlchemy + SQLite 的笔记 REST API。W2 练手项目：把「Pydantic 模型 + 数据库 + 依赖注入 + 测试」这套后端核心动作跑一遍。

## 技术栈

| 层 | 工具 |
|---|---|
| Web 框架 | FastAPI |
| 参数校验 / 序列化 | Pydantic v2 |
| ORM | SQLAlchemy 2.0 |
| 数据库 | SQLite（后期换 PostgreSQL） |
| 测试 | pytest + httpx2（TestClient） |
| 代码检查 | ruff |

## 安装与运行

```powershell
cd D:\deepseek\agent-portfolio\notes-api
uv sync
uv run uvicorn notes_api.main:app --reload --port 8000
```

打开 http://127.0.0.1:8000/docs 可以直接在浏览器里试所有接口。

## 接口

| 方法 | 路径 | 说明 | 成功状态码 |
|---|---|---|---|
| GET | `/health` | 健康检查 | 200 |
| POST | `/notes` | 新建笔记 | 201 |
| GET | `/notes` | 列出所有笔记 | 200 |
| GET | `/notes/{id}` | 查单条 | 200 / 404 |
| PATCH | `/notes/{id}` | 部分更新 | 200 / 404 |
| DELETE | `/notes/{id}` | 删除 | 204 / 404 |

请求示例：

```json
POST /notes
{ "title": "第一条笔记", "content": "今天学了 SQLAlchemy" }
```

## 目录结构

```
notes-api/
├─ src/notes_api/
│  ├─ main.py            # 应用入口（lifespan 建表）
│  ├─ db.py              # 引擎、会话、Base、get_db 依赖
│  ├─ models.py          # ORM 模型（notes 表）
│  ├─ schemas.py         # Pydantic 模型（入参/出参）
│  └─ routers/notes.py   # 笔记相关路由
├─ tests/
│  ├─ conftest.py        # 每个测试用独立的临时数据库
│  ├─ test_health.py
│  └─ test_notes.py
└─ pyproject.toml
```

## 开发

```powershell
uv run pytest          # 12 个测试
uv run ruff check .    # 代码检查
uv run ruff format .   # 自动格式化
```

## 设计说明

1. **三层分离**：`models`（数据库表）↔ `schemas`（接口出入参）↔ `routers`（业务逻辑）。数据库结构变了不会直接影响接口契约。
2. **依赖注入**：`get_db()` 每个请求给一个 Session，请求结束自动关闭；测试里用 `dependency_overrides` 换成临时数据库。
3. **状态码语义**：创建用 201，删除用 204，查不到用 404，参数不合法交给 Pydantic 返回 422。
4. **建表用 `create_all`**：教学阶段够用；下一阶段会换成 Alembic 迁移（改表结构不丢数据）。
