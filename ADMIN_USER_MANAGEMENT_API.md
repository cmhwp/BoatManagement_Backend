# 管理员用户管理API文档

## 概述
本文档描述了管理员对用户进行增删改查和状态管理的完整API接口。

## 基础信息
- **基础路径**: `/api/v1/admin`
- **权限要求**: 管理员角色 (ADMIN)
- **认证方式**: Bearer Token

## 用户管理接口

### 1. 创建用户
**POST** `/api/v1/admin/users`

创建新用户账户。

**请求体**:
```json
{
  "username": "string",
  "email": "user@example.com",
  "phone": "string",
  "password": "string",
  "real_name": "string",
  "gender": "string",
  "address": "string",
  "role": "user"
}
```

**响应**:
```json
{
  "success": true,
  "message": "用户创建成功",
  "data": {
    "id": 1,
    "username": "string",
    "email": "user@example.com",
    "phone": "string",
    "role": "user",
    "status": "active",
    "is_verified": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### 2. 获取用户列表
**GET** `/api/v1/admin/users`

获取所有用户的分页列表，支持多种筛选条件。

**查询参数**:
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 20, 最大: 100)
- `role`: 用户角色筛选 (admin/merchant/user/crew)
- `status`: 用户状态筛选 (active/inactive/suspended/deleted)
- `is_verified`: 是否已实名认证筛选 (true/false)
- `search`: 搜索关键词 (用户名、邮箱、真实姓名、手机号)

**响应**:
```json
{
  "success": true,
  "message": "获取成功",
  "data": [...],
  "total": 100,
  "page": 1,
  "size": 20
}
```

### 3. 获取用户详情
**GET** `/api/v1/admin/users/{user_id}`

获取指定用户的详细信息。

**响应**:
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "id": 1,
    "username": "string",
    "email": "user@example.com",
    "role": "user",
    "status": "active",
    "is_verified": false,
    "last_login_at": "2024-01-01T00:00:00Z"
  }
}
```

### 4. 更新用户信息
**PUT** `/api/v1/admin/users/{user_id}`

更新指定用户的基本信息。

**请求体**:
```json
{
  "username": "string",
  "email": "user@example.com",
  "phone": "string",
  "real_name": "string",
  "gender": "string",
  "address": "string",
  "avatar": "string"
}
```

## 用户状态管理

### 5. 更新用户状态
**PUT** `/api/v1/admin/users/{user_id}/status`

更新用户的状态。

**请求体**:
```json
{
  "new_status": "active|inactive|suspended|deleted"
}
```

**安全限制**:
- 不能修改自己的状态
- 不能暂停或删除管理员账户

### 6. 激活用户
**POST** `/api/v1/admin/users/{user_id}/activate`

将用户状态设置为激活。

### 7. 暂停用户
**POST** `/api/v1/admin/users/{user_id}/suspend`

将用户状态设置为暂停。

**安全限制**:
- 不能暂停自己
- 不能暂停管理员账户

### 8. 软删除用户
**POST** `/api/v1/admin/users/{user_id}/soft-delete`

将用户状态设置为已删除（软删除）。

**安全限制**:
- 不能删除自己
- 不能删除管理员账户

## 用户删除操作

### 9. 物理删除用户
**DELETE** `/api/v1/admin/users/{user_id}`

从数据库中完全删除用户记录。

**响应**:
```json
{
  "success": true,
  "message": "用户删除成功",
  "data": {
    "deleted_user_id": 1
  }
}
```

**安全限制**:
- 不能删除自己
- 不能删除管理员账户

## 批量操作

### 10. 批量用户操作
**POST** `/api/v1/admin/users/batch-operation`

对多个用户执行批量操作。

**查询参数**:
- `user_ids`: 用户ID列表 (必需)
- `operation`: 操作类型 - activate/suspend/soft_delete

**请求示例**:
```
POST /api/v1/admin/users/batch-operation?user_ids=1&user_ids=2&user_ids=3&operation=activate
```

**响应**:
```json
{
  "success": true,
  "message": "成功激活了 3 个用户",
  "data": {
    "operation": "activate",
    "affected_count": 3,
    "user_ids": [1, 2, 3]
  }
}
```

**安全限制**:
- 不能对自己执行批量操作
- 对管理员的暂停和软删除操作会被拒绝

## 角色和认证管理

### 11. 更新用户角色
**PUT** `/api/v1/admin/users/{user_id}/role`

更新用户的角色。

**请求体**:
```json
{
  "new_role": "admin|merchant|user|crew"
}
```

**安全限制**:
- 不能修改自己的角色

### 12. 用户实名认证管理
**PUT** `/api/v1/admin/users/{user_id}/verify`

管理用户的实名认证状态。

**查询参数**:
- `is_verified`: 是否验证 (true/false)

## 统计和监控

### 13. 管理员仪表板
**GET** `/api/v1/admin/dashboard`

获取管理员仪表板的综合数据。

**响应**:
```json
{
  "success": true,
  "data": {
    "user_stats": {
      "total_users": 100,
      "recent_users": 5,
      "active_users": 95
    },
    "merchant_stats": {
      "total_merchants": 20,
      "verified_merchants": 18,
      "verification_rate": 90.0
    },
    "crew_stats": {
      "total_crews": 15,
      "available_crews": 12,
      "availability_rate": 80.0
    },
    "boat_stats": {
      "total_boats": 30,
      "available_boats": 25,
      "availability_rate": 83.33
    }
  }
}
```

### 14. 用户状态汇总
**GET** `/api/v1/admin/users/status-summary`

获取用户状态的详细统计信息。

**响应**:
```json
{
  "success": true,
  "data": {
    "total_users": 100,
    "status_distribution": {
      "active": {"count": 85, "percentage": 85.0},
      "inactive": {"count": 10, "percentage": 10.0},
      "suspended": {"count": 3, "percentage": 3.0},
      "deleted": {"count": 2, "percentage": 2.0}
    },
    "role_status_matrix": {
      "admin": {"active": 5, "inactive": 0, "suspended": 0, "deleted": 0},
      "merchant": {"active": 18, "inactive": 2, "suspended": 1, "deleted": 0},
      "user": {"active": 55, "inactive": 8, "suspended": 2, "deleted": 2},
      "crew": {"active": 7, "inactive": 0, "suspended": 0, "deleted": 0}
    },
    "verification_summary": {
      "verified": 75,
      "unverified": 25,
      "verification_rate": 75.0
    },
    "active_user_rate": 85.0
  }
}
```

### 15. 最近用户活动统计
**GET** `/api/v1/admin/users/recent-activities`

获取最近一段时间的用户活动统计。

**查询参数**:
- `days`: 查询最近天数 (1-30, 默认: 7)

**响应**:
```json
{
  "success": true,
  "data": {
    "date_range": {
      "start_date": "2024-01-01T00:00:00Z",
      "end_date": "2024-01-08T00:00:00Z",
      "days": 7
    },
    "recent_registrations": 5,
    "recent_logins": 45,
    "active_users": 40,
    "role_registration_breakdown": {
      "admin": 0,
      "merchant": 1,
      "user": 3,
      "crew": 1
    },
    "activity_rate": 900.0
  }
}
```

### 16. 系统统计信息
**GET** `/api/v1/admin/system/stats`

获取系统的整体统计信息。

**响应**:
```json
{
  "success": true,
  "data": {
    "role_distribution": {
      "admin": 5,
      "merchant": 20,
      "user": 70,
      "crew": 15
    },
    "status_distribution": {
      "active": 85,
      "inactive": 10,
      "suspended": 3,
      "deleted": 2
    },
    "verification_stats": {
      "verified": 75,
      "unverified": 25,
      "verification_rate": 75.0
    }
  }
}
```

## 错误响应

所有接口在出错时返回统一的错误格式：

```json
{
  "success": false,
  "message": "错误描述",
  "detail": "详细错误信息"
}
```

常见错误状态码：
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误

## 权限控制总结

### 管理员不能执行的操作：
1. 修改自己的状态、角色
2. 删除自己的账户
3. 对自己执行批量操作
4. 暂停、删除其他管理员账户

### 安全机制：
1. 所有操作都需要管理员权限验证
2. 重要操作有额外的权限检查
3. 批量操作会验证每个目标用户的权限
4. 操作日志记录状态变更

## 使用示例

### 创建用户
```bash
curl -X POST "http://localhost:8000/api/v1/admin/users" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123",
    "role": "user"
  }'
```

### 批量激活用户
```bash
curl -X POST "http://localhost:8000/api/v1/admin/users/batch-operation?user_ids=1&user_ids=2&operation=activate" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 获取用户状态汇总
```bash
curl -X GET "http://localhost:8000/api/v1/admin/users/status-summary" \
  -H "Authorization: Bearer YOUR_TOKEN"
``` 