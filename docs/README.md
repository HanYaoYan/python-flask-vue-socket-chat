# 文档索引

本目录包含项目的技术文档。

## 📚 文档列表

### 核心文档

- **[项目主文档](../README.md)** - 项目概述、技术栈、API 文档、快速开始
- **[Docker 一键启动指南](../README_DOCKER.md)** - Docker 完整部署和启动说明（推荐使用）

### 技术参考

- **[项目结构说明](PROJECT_STRUCTURE.md)** - 详细的目录结构和文件组织说明

## 🚀 快速开始

### 最简单的方式（推荐）

**Windows:**
```cmd
启动.bat
```

**Linux/macOS:**
```bash
chmod +x 启动.sh
./启动.sh
```

这将启动所有服务（MySQL、Redis、后端、前端），访问地址：
- 前端：http://localhost:5173
- 后端 API：http://localhost:9000

### 本地开发方式

如果你已经在本地安装了 Node.js 和 Python，可以按照 `README.md` 中的"本地开发启动"部分进行操作。

## 📖 文档说明

- 所有文档使用 Markdown 格式
- 建议使用支持 Markdown 的编辑器查看
- 项目主文档和 Docker 指南包含所有必要的启动和部署信息
