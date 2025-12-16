# Desktop Chat Application

基于 Electron + Vue 3 + Flask + MySQL + Redis 的桌面端在线聊天室应用

## 技术栈

### 前端
- **Electron** - 跨平台桌面应用框架
- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Pinia** - Vue 状态管理
- **Socket.IO Client** - 实时通信客户端

### 后端
- **Flask** - Python Web 框架
- **Flask-SocketIO** - WebSocket 支持
- **SQLAlchemy** - ORM 框架
- **MySQL 8.0** - 关系型数据库
- **Redis 6.0** - 内存数据库（缓存和在线状态）

## 核心功能

- ✅ 用户注册/登录（JWT 认证）
- ✅ 实时群聊
- ✅ 私聊（基础支持）
- ✅ 在线状态同步
- ✅ 历史消息分页查询
- ✅ WebSocket 自动重连
- ✅ 消息实时推送
- ✅ 房间创建和管理

## 项目结构

```
.
├── app.py                 # Flask 主应用
├── config.py              # 配置文件
├── models/                # 数据模型
│   ├── user.py           # 用户模型
│   ├── message.py        # 消息模型
│   └── room.py           # 房间模型
├── routes/                # 路由模块
│   ├── auth.py           # 认证路由
│   ├── rooms.py          # 房间路由
│   └── users.py          # 用户路由
├── utils/                 # 工具模块
│   └── redis_client.py   # Redis 客户端
├── frontend/              # 前端项目
│   ├── src/
│   │   ├── api/          # API 接口
│   │   ├── components/   # Vue 组件
│   │   ├── router/       # 路由配置
│   │   ├── store/        # 状态管理
│   │   ├── utils/        # 工具函数
│   │   └── views/        # 页面视图
│   ├── electron/         # Electron 主进程
│   └── package.json
├── docker-compose.yml     # Docker Compose 配置
├── Dockerfile            # Docker 镜像配置
├── requirements.txt      # Python 依赖
└── .env.example          # 环境变量示例
```

## 环境要求

- Python >= 3.8
- Node.js >= 16.0
- MySQL >= 8.0
- Redis >= 6.0

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd python-flask-vue-socket-chat
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接等信息。

### 3. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 4. 启动 MySQL 和 Redis

#### 方式一：使用 Docker Compose（推荐）

```bash
docker-compose up -d mysql redis
```

#### 方式二：本地安装

确保 MySQL 和 Redis 服务已启动，并在 `.env` 中配置正确的连接信息。

### 5. 初始化数据库

首次运行应用会自动创建数据库表：

```bash
python app.py
```

或手动创建数据库：

```sql
CREATE DATABASE chat_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. 启动后端服务

```bash
python app.py
```

后端服务将在 `http://localhost:9000` 启动。

### 7. 安装前端依赖

```bash
cd frontend
npm install
```

### 8. 启动前端开发服务器

```bash
npm run dev
```

前端开发服务器将在 `http://localhost:5173` 启动。

### 9. 启动 Electron 桌面应用

```bash
npm run electron:dev
```

## 生产环境部署

### 构建前端

```bash
cd frontend
npm run build
```

### 构建桌面应用

#### Windows
```bash
npm run electron:build:win
```

#### macOS
```bash
npm run electron:build:mac
```

#### Linux
```bash
npm run electron:build:linux
```

构建产物将在 `frontend/dist-electron` 目录。

### 使用 Docker 部署后端

```bash
docker-compose up -d
```

这将启动 MySQL、Redis 和应用服务。

## API 文档

### 认证接口

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/verify` - 验证 Token

### 房间接口

- `GET /api/rooms/` - 获取房间列表
- `POST /api/rooms/` - 创建房间
- `POST /api/rooms/<room_id>/join` - 加入房间
- `GET /api/rooms/<room_id>/messages` - 获取房间消息（分页）

### 用户接口

- `GET /api/users/online` - 获取在线用户列表
- `GET /api/users/search` - 搜索用户

### WebSocket 事件

#### 客户端发送

- `join_room` - 加入房间
- `leave_room` - 离开房间
- `send_message` - 发送消息

#### 服务器推送

- `new_message` - 新消息
- `user_online` - 用户上线
- `user_offline` - 用户下线
- `joined_room` - 加入房间成功
- `error` - 错误信息

## 性能优化

- ✅ 消息先写入 MySQL，再更新 Redis 缓存（数据一致性）
- ✅ Redis 缓存最新 50 条消息，加速首屏加载
- ✅ 在线状态通过 Redis Set 管理，支持快速查询
- ✅ WebSocket 自动重连机制，保障连接稳定性
- ✅ 历史消息分页查询，避免一次性加载过多数据

## 数据存储策略

- **MySQL**: 存储用户、消息、房间等持久化数据
- **Redis**: 
  - 缓存用户在线状态（过期时间 5 分钟）
  - 缓存房间最新消息（50 条，过期时间 1 小时）
  - 存储在线用户列表

## 注意事项

1. 首次运行前需确保 MySQL 和 Redis 服务已启动
2. 生产环境请修改 `.env` 中的 `SECRET_KEY` 和 `JWT_SECRET_KEY`
3. 桌面应用需要后端服务运行在 `http://localhost:9000`（开发环境）
4. 支持 10-50 人同时在线，如需更高并发请优化配置

## 故障排查

### 数据库连接失败

检查 MySQL 服务是否启动，以及 `.env` 中的数据库配置是否正确。

### Redis 连接失败

检查 Redis 服务是否启动，以及 `.env` 中的 Redis 配置是否正确。

### WebSocket 连接失败

检查后端服务是否运行，以及防火墙是否允许 WebSocket 连接。

## 开发计划

- [ ] 私聊功能完善
- [ ] 消息已读/未读状态
- [ ] 文件传输支持
- [ ] 消息搜索功能
- [ ] 用户头像上传
- [ ] 消息撤回功能

## 许可证

[LICENSE](LICENSE)
