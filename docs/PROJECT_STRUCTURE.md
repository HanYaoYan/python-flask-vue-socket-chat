# 项目结构说明

本文档详细说明项目的目录结构和文件组织。

## 📁 目录结构

```
python-flask-vue-socket-chat/
│
├── 📄 app.py                      # Flask 主应用入口
├── 📄 config.py                   # 应用配置文件（读取环境变量）
├── 📄 requirements.txt            # Python 依赖包列表
├── 📄 wait-for-mysql.py           # MySQL 启动等待脚本
├── 📄 init_db.py                  # 数据库初始化脚本（可选）
├── 📄 .env.example                # 环境变量配置示例
├── 📄 README.md                   # 项目主文档
│
├── 📂 models/                     # 数据模型层
│   ├── __init__.py
│   ├── user.py                   # 用户模型
│   ├── message.py                # 消息模型
│   └── room.py                   # 房间模型
│
├── 📂 routes/                     # 路由层（API 端点）
│   ├── __init__.py
│   ├── auth.py                   # 认证相关路由（注册、登录、验证）
│   ├── rooms.py                  # 房间相关路由（创建、加入、列表、消息）
│   └── users.py                  # 用户相关路由（在线用户、搜索）
│
├── 📂 utils/                      # 工具模块
│   ├── __init__.py
│   └── redis_client.py           # Redis 客户端封装
│
├── 📂 frontend/                   # 前端项目（Vue 3 + Electron）
│   ├── 📄 package.json           # 前端依赖和脚本配置
│   ├── 📄 vite.config.js         # Vite 构建配置
│   ├── 📄 index.html             # HTML 入口文件
│   │
│   ├── 📂 electron/              # Electron 主进程
│   │   └── main.js              # Electron 窗口配置
│   │
│   ├── 📂 src/                   # 前端源代码
│   │   ├── main.js              # Vue 应用入口
│   │   ├── App.vue              # 根组件
│   │   ├── style.css            # 全局样式
│   │   │
│   │   ├── 📂 api/              # API 接口封装
│   │   │   ├── request.js      # Axios 请求配置
│   │   │   ├── auth.js         # 认证 API
│   │   │   ├── rooms.js        # 房间 API
│   │   │   └── users.js        # 用户 API
│   │   │
│   │   ├── 📂 components/       # Vue 组件
│   │   │   └── CreateRoomModal.vue
│   │   │
│   │   ├── 📂 router/           # 路由配置
│   │   │   └── index.js        # Vue Router 配置
│   │   │
│   │   ├── 📂 store/            # 状态管理（Pinia）
│   │   │   ├── auth.js         # 认证状态
│   │   │   └── chat.js         # 聊天状态
│   │   │
│   │   ├── 📂 utils/            # 工具函数
│   │   │   └── socket.js       # Socket.IO 客户端封装
│   │   │
│   │   └── 📂 views/            # 页面视图
│   │       ├── Login.vue       # 登录页面
│   │       ├── Register.vue    # 注册页面
│   │       └── Chat.vue        # 聊天页面
│   │
│   └── 📂 node_modules/          # 前端依赖包（npm install 后生成）
│
├── 📂 docs/                       # 📚 项目文档
│   ├── README.md                 # 文档索引
│   │
│   ├── 📂 deployment/            # 部署相关文档
│   │   └── DEPLOYMENT.md        # 部署指南
│   │
│   ├── 📂 docker/                # Docker 相关文档
│   │   ├── DOCKER.md            # Docker 部署指南
│   │   ├── DOCKER_BUILD.md      # 镜像构建说明
│   │   ├── DOCKER_MIRROR_SETUP.md  # 镜像加速配置
│   │   └── DOCKER_TROUBLESHOOTING.md  # 故障排查
│   │
│   └── 📂 guides/                # 使用指南
│       ├── README_QUICKSTART.md  # 快速启动指南
│       ├── START.md              # 启动说明
│       ├── 启动说明.md           # 中文启动说明
│       └── 前端启动检查清单.md   # 前端检查清单
│
├── 📂 static/                     # 静态文件（已弃用，前端使用 npm 包管理）
│
├── 📂 templates/                  # HTML 模板（已弃用，前端使用 Vue SPA）
│
├── 📄 docker-compose.yml          # Docker Compose 配置（官方镜像）
├── 📄 docker-compose.cn.yml       # Docker Compose 配置（国内镜像，已弃用）
├── 📄 Dockerfile                  # Docker 镜像构建文件（官方镜像源）
├── 📄 Dockerfile.cn               # Docker 镜像构建文件（国内镜像源）
├── 📄 docker-daemon.json.example  # Docker 镜像加速配置示例
│
└── 📄 LICENSE                     # 许可证文件
```

## 📋 代码文件说明

### 后端核心文件

| 文件 | 说明 |
|------|------|
| `app.py` | Flask 应用主入口，初始化数据库、Socket.IO、路由注册 |
| `config.py` | 配置管理，从环境变量读取配置 |
| `models/` | SQLAlchemy 数据模型定义 |
| `routes/` | Flask 蓝图，定义 RESTful API 端点 |
| `utils/redis_client.py` | Redis 客户端封装，管理在线状态和消息缓存 |

### 前端核心文件

| 文件/目录 | 说明 |
|----------|------|
| `frontend/src/main.js` | Vue 应用入口，初始化 Pinia 和 Router |
| `frontend/src/App.vue` | 根组件，包含路由视图 |
| `frontend/src/router/` | 路由配置，包括路由守卫 |
| `frontend/src/store/` | Pinia 状态管理，管理认证和聊天状态 |
| `frontend/src/api/` | API 接口封装，使用 Axios |
| `frontend/src/utils/socket.js` | Socket.IO 客户端封装 |
| `frontend/src/views/` | 页面组件（登录、注册、聊天） |

### 配置文件

| 文件 | 说明 |
|------|------|
| `requirements.txt` | Python 依赖包列表 |
| `frontend/package.json` | 前端依赖和 npm 脚本 |
| `frontend/vite.config.js` | Vite 构建配置，包括代理设置 |
| `.env.example` | 环境变量配置示例 |
| `docker-compose.yml` | Docker Compose 服务编排 |
| `Dockerfile` | Docker 镜像构建配置 |

## 📚 文档文件说明

所有文档已整理到 `docs/` 目录下，按功能分类：

- **`docs/README.md`** - 文档索引，快速导航所有文档
- **`docs/guides/`** - 使用指南，快速启动和常见问题
- **`docs/docker/`** - Docker 相关文档，部署和故障排查
- **`docs/deployment/`** - 部署文档，生产环境配置

## 🎯 代码组织原则

1. **前后端分离**：前端代码在 `frontend/`，后端代码在根目录
2. **分层架构**：后端采用 MVC 模式（models, routes, views）
3. **模块化**：功能按模块组织（auth, rooms, users）
4. **文档集中**：所有文档集中在 `docs/` 目录
5. **配置分离**：配置通过环境变量管理，示例文件 `.env.example`

## 📝 开发规范

- **Python**: 遵循 PEP 8 代码风格
- **JavaScript**: 使用 ES6+ 语法，遵循 Vue 3 最佳实践
- **文档**: 使用 Markdown 格式，保持更新
- **提交**: 提交前确保代码格式化和测试通过

## 🔍 快速定位

- **修改后端 API** → `routes/` 目录
- **修改数据模型** → `models/` 目录
- **修改前端页面** → `frontend/src/views/` 目录
- **修改前端组件** → `frontend/src/components/` 目录
- **修改 API 接口** → `frontend/src/api/` 目录
- **查看文档** → `docs/` 目录

