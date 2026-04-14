# Unity 游戏 API 服务器

这是一个简单的 Unity HTTP 服务器实现，用于让外部程序（如 AI 测试系统）控制 Unity 游戏。

## 文件说明

| 文件 | 说明 |
|------|------|
| `UnityGameServer.cs` | 游戏服务器主类，提供游戏控制接口 |
| `HttpServer.cs` | HTTP 服务器实现，处理外部请求 |
| `JsonHelper.cs` | JSON 序列化/反序列化辅助类 |

## 使用方法

### 1. 在 Unity 项目中导入脚本

将这三个 `.cs` 文件复制到 Unity 项目的 `Assets/Scripts` 目录下。

### 2. 创建服务器对象

在场景中创建一个空 GameObject，命名为 `GameServer`，然后添加 `UnityGameServer` 组件：

```csharp
// 在场景中添加以下代码（可选）
public class GameInitializer : MonoBehaviour
{
    void Start()
    {
        // 可以通过代码启动服务器
        // HttpServer server = gameObject.AddComponent<HttpServer>();
        // server.port = 8080;
    }
}
```

### 3. 配置服务器

在 Inspector 中配置：
- **Port**: 服务器端口（默认 8080）
- **API Key**: 可选的 API 认证密钥

### 4. 运行游戏

启动 Unity 游戏，服务器会在指定端口运行。

## API 端点

### GET /status
获取服务器状态

**响应示例：**
```json
{
  "status": "running",
  "port": 8080,
  "game_active": true
}
```

### POST /reset
重置游戏

**请求体：**
```json
{
  "level_id": "level1"
}
```

**响应示例：**
```json
{
  "success": true,
  "level": "level1",
  "state": {
    "steps": 0,
    "is_running": true,
    "reward": 0
  }
}
```

### POST /step
执行动作

**请求体：**
```json
{
  "action": "MOVE_FORWARD"
}
```

**响应示例：**
```json
{
  "success": true,
  "action": "MOVE_FORWARD",
  "state": {
    "steps": 1,
    "is_running": true,
    "reward": 0
  },
  "reward": 0,
  "done": false
}
```

### GET /valid_actions
获取合法动作列表

**响应示例：**
```json
{
  "actions": [
    "MOVE_FORWARD", "MOVE_BACKWARD", "MOVE_LEFT", "MOVE_RIGHT",
    "JUMP", "ATTACK", "INTERACT"
  ]
}
```

### POST /render
获取屏幕截图

**响应示例：**
```json
{
  "success": true,
  "image": "base64_encoded_image_data",
  "width": 1920,
  "height": 1080
}
```

## Python 客户端示例

```python
import requests
import json

BASE_URL = "http://localhost:8080"

# 获取状态
response = requests.get(f"{BASE_URL}/status")
print(response.json())

# 重置游戏
response = requests.post(f"{BASE_URL}/reset", json={"level_id": "level1"})
print(response.json())

# 执行动作
response = requests.post(f"{BASE_URL}/step", json={"action": "MOVE_FORWARD"})
print(response.json())

# 获取合法动作
response = requests.get(f"{BASE_URL}/valid_actions")
print(response.json())
```

## 注意事项

1. **防火墙**：确保防火墙允许 Unity 访问网络
2. **端口冲突**：确保指定端口没有被其他程序占用
3. **性能**：HTTP 请求会有一定的延迟，适合步进式游戏测试
4. **安全性**：生产环境建议设置 API Key 进行认证

## 扩展功能

可以扩展以下功能：
- WebSocket 支持（实时通信）
- 多游戏支持（通过路径区分）
- 游戏录制/回放
- 性能监控
