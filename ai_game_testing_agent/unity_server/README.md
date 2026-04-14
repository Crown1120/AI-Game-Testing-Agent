# Unity 服务器配置示例

将以下脚本附加到场景中的 GameObject 上：

## 使用步骤

### 1. 添加服务器组件

```csharp
// 在场景中创建一个空 GameObject，命名为 "GameServer"
// 将 SimpleHttpServer.cs 脚本添加到该对象
```

### 2. 配置服务器参数

在 Inspector 中设置：
- Port: 8080 (默认端口)
- API Key: (可选) 设置 API 认证密钥

### 3. 实现游戏特定逻辑

在 `SimpleHttpServer.cs` 中实现你的游戏逻辑：

```csharp
void ExecuteAction(string action)
{
    // 根据动作执行相应操作
    switch (action)
    {
        case "UP":
            player.transform.Translate(Vector3.up);
            break;
        case "DOWN":
            player.transform.Translate(Vector3.down);
            break;
        case "LEFT":
            player.transform.Translate(Vector3.left);
            break;
        case "RIGHT":
            player.transform.Translate(Vector3.right);
            break;
    }
}
```

### 4. 运行游戏

构建并运行游戏，服务器将自动启动。

### 5. 从 Python 连接

```python
from game_env import Unity3DEnv

env = Unity3DEnv(
    api_url="http://localhost:8080",
    api_key=None  # 如果设置了 API Key，请填入
)

# 重置游戏
env.reset()

# 执行动作
state, reward, done, info = env.step("UP")
```

## API 端点说明

| 端点 | 方法 | 描述 |
|------|------|------|
| `/status` | GET | 获取服务器状态 |
| `/reset` | POST | 重置游戏 |
| `/step` | POST | 执行动作 |
| `/valid_actions` | POST | 获取合法动作列表 |
| `/render` | POST | 获取屏幕截图 |

## 响应格式

### 成功响应
```json
{
    "success": true,
    "message": "Action Executed",
    "data": {}
}
```

### 错误响应
```json
{
    "success": false,
    "message": "Error description"
}
```
