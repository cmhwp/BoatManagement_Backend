# 绿色智能船艇农文旅服务平台后端

基于FastAPI构建的绿色智能船艇农文旅服务平台后端系统，集成用户管理、商家管理、船艇调度、服务预订、农产品销售等功能。

## 技术栈

- **FastAPI**: 现代高性能的Python Web框架
- **SQLAlchemy**: Python SQL工具包和ORM
- **MySQL**: 关系型数据库
- **Redis**: 内存数据库，用于缓存和会话管理
- **JWT**: JSON Web Token，用于用户认证
- **Pydantic**: 数据验证和设置管理
- **Alembic**: 数据库迁移工具

## 项目结构

```
├── app/
│   ├── config.py          # 配置文件
│   ├── crud/              # 数据库操作
│   ├── db/                # 数据库连接
│   ├── models/            # 数据库模型
│   ├── routers/           # API路由
│   ├── schemas/           # Pydantic模式
│   └── utils/             # 工具函数
├── alembic/               # 数据库迁移文件
├── alembic.ini           # Alembic配置
├── main.py               # 主应用文件
├── requirements.txt      # 依赖包
└── README.md             # 项目说明
```

## 安装与运行

### 1. 环境要求

- Python 3.8+
- MySQL 5.7+
- Redis 6.0+

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件并配置以下参数：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/boat_management_db
DB_HOST=localhost
DB_PORT=3306
DB_USER=username
DB_PASSWORD=password
DB_NAME=boat_management_db

# JWT配置
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 应用配置
APP_NAME=绿色智能船艇农文旅服务平台
APP_VERSION=1.0.0
DEBUG=True
```

### 4. 初始化数据库

```bash
# 创建数据库迁移
alembic init alembic

# 生成迁移文件
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 5. 运行服务

```bash
# 开发环境
python main.py

# 或使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API文档

启动服务后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 核心功能

### 用户管理
- 用户注册/登录
- 角色申请（商家/船员）
- 用户信息管理

### 商家管理
- 商家资质认证
- 船艇管理
- 服务项目管理
- 农产品管理

### 船艇调度
- 船艇状态监控
- GPS定位追踪
- 智能调度算法

### 订单管理
- 服务预订
- 农产品购买
- 套餐组合

### 农产品管理
- 产品信息管理
- 库存管理
- 有机认证

## 数据库设计

系统包含11个核心表：

1. **用户表 (users)**: 用户基本信息和角色
2. **角色申请表 (role_applications)**: 商家/船员角色申请
3. **商家信息表 (merchants)**: 商家认证信息
4. **船员信息表 (crew_info)**: 船员认证信息
5. **船艇表 (boats)**: 船艇基本信息和状态
6. **服务项目表 (services)**: 旅游服务项目
7. **农产品表 (agricultural_products)**: 农产品信息
8. **服务-产品组合表 (service_product_bundles)**: 套餐组合
9. **订单表 (orders)**: 订单信息
10. **库存变更表 (inventory_logs)**: 库存变更记录
11. **管理员表 (admins)**: 系统管理员

## 部署说明

### 1. 生产环境配置

- 修改 `SECRET_KEY` 为强密码
- 配置正确的数据库连接信息
- 设置 `DEBUG=False`
- 配置CORS允许的域名

### 2. Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 开发规范

- 遵循PEP 8编码规范
- 使用类型注解
- 编写完整的API文档
- 进行单元测试

## 许可证

MIT License 