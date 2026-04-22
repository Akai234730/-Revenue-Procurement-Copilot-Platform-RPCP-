# 本地运行说明

## 1. 启动数据库

```bash
docker compose up -d postgres
```

## 2. 启动后端

```bash
cd apps/api
python -m venv .venv
.venv\\Scripts\\activate
pip install -e .[dev]
copy .env.example .env
python -m app.run
```

## 3. 启动前端

```bash
cd apps/web
npm install
npm run dev
```

## 4. 访问地址
- 前端：`http://localhost:5173`
- 后端：`http://localhost:8000/api/v1/health`

## 5. 当前实现说明
当前已完成企业级基础骨架：
- 后端基础架构
- 四大业务域 API 骨架
- 前端企业级工作台骨架
- 知识中心、运营中心、设置中心基础页面
- Docker 与 compose 基础文件

下一步应继续推进：
- 真正数据库迁移补全
- 真实鉴权与 RBAC
- 领域服务与仓储层
- 审计持久化
- AI 编排与知识检索真实接入
- 测试体系扩展
