# 绿色智能船艇农文旅平台

基于FastAPI框架开发的绿色智能船艇农文旅平台后端API系统。

## 项目特色

- 🚤 **智能船艇管理**: 实时船艇状态监控和管理
- 🌾 **农业观光服务**: 农业基地游览和农产品展示
- 🏛️ **文化体验**: 传统文化展示和体验活动
- 🏝️ **旅游服务**: 完整的旅游路线和景点管理
- 👥 **多角色系统**: 支持管理员、商家、用户、船员四种角色

## 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: MySQL
- **ORM**: SQLAlchemy 2.0.23
- **认证**: JWT (JSON Web Tokens)
- **密码加密**: bcrypt
- **API文档**: Swagger/OpenAPI

## 项目结构

```
BoatManagement_Backend/
├── app/
│   ├── config/         # 配置模块
│   │   ├── settings.py # 应用配置
│   │   └── database.py # 数据库配置
│   ├── models/         # 数据模型
│   │   ├── user.py     # 用户模型
│   │   └── enums.py    # 枚举定义
│   ├── schemas/        # Pydantic模式
│   │   └── user.py     # 用户模式定义
│   ├── crud/           # 数据库操作
│   │   └── user.py     # 用户CRUD操作
│   ├── routers/        # API路由
│   │   ├── auth.py     # 认证路由
│   │   └── users.py    # 用户管理路由
│   ├── utils/          # 工具模块
│   │   ├── security.py # 安全工具
│   │   └── deps.py     # 依赖项
│   └── services/       # 业务逻辑服务
├── main.py             # 主应用文件
├── requirements.txt    # 项目依赖
└── README.md          # 项目说明
```

## 安装和运行

### 1. 克隆项目

```bash
git clone <repository-url>
cd BoatManagement_Backend
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

创建MySQL数据库：

```sql
CREATE DATABASE boat_tour_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

修改 `app/config/settings.py` 中的数据库连接配置：

```python
database_url: str = "mysql+pymysql://用户名:密码@localhost:3306/boat_tour_db"
```

### 4. 运行应用

```bash
python main.py
```

或使用uvicorn：

```bash
uvicorn main:app --reload
```

应用将在 http://localhost:8000 启动

## API文档

启动应用后，可以访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 用户角色

| 角色 | 权限描述 |
|------|----------|
| **admin** | 管理员 - 拥有系统所有权限 |
| **merchant** | 商家 - 船艇服务提供商，可管理自己的服务 |
| **user** | 普通用户 - 游客用户，可预订服务 |
| **crew** | 船员 - 船艇操作人员，可操作船艇相关功能 |

## 已实现功能

✅ **用户认证系统**
- 用户注册
- 用户登录
- JWT令牌认证
- 用户信息管理
- 角色权限控制

✅ **基础架构**
- FastAPI应用配置
- MySQL数据库连接
- CORS跨域配置
- API文档生成

## 开发中功能

🔄 **船艇管理系统**
- 船艇信息管理
- 船艇状态监控
- 船艇位置追踪

🔄 **农文旅服务系统**
- 旅游路线管理
- 农业基地管理
- 文化活动管理
- 预订系统

## API接口示例

### 用户注册

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "123456",
       "role": "user"
     }'
```

### 用户登录

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "password": "123456"
     }'
```

### 获取用户信息

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
     -H "Authorization: Bearer <your-token>"
```

## 开发计划

请查看 `.cursorrules` 文件了解详细的开发进度和计划。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

本项目采用MIT许可证。 