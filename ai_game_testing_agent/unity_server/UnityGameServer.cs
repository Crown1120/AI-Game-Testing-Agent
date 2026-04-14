using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;

/// <summary>
/// Unity 游戏服务器组件
/// 用于接收外部测试系统的控制命令
/// </summary>
[RequireComponent(typeof(UnityGameServer))]
public class UnityGameServer : MonoBehaviour
{
    [Header("服务器配置")]
    public int port = 8080;
    public string apiKey = "";

    [Header("游戏对象引用")]
    public GameObject player;
    public List<GameObject> boxes;
    public List<GameObject> goals;

    private HttpListener _listener;
    private bool _isRunning = false;

    void Start()
    {
        StartServer();
    }

    void OnDestroy()
    {
        StopServer();
    }

    public void StartServer()
    {
        if (_isRunning) return;

        // 启动 HTTP 服务器协程
        StartCoroutine(HttpServerCoroutine());
        Debug.Log($"[UnityGameServer] 服务器已启动，端口: {port}");
        _isRunning = true;
    }

    public void StopServer()
    {
        _isRunning = false;
        Debug.Log("[UnityGameServer] 服务器已停止");
    }

    IEnumerator HttpServerCoroutine()
    {
        // 简单实现：使用 UnityWebRequest 作为测试
        // 实际生产环境建议使用 SuperSocket 或 HttpListener
        yield return null;
    }

    // API 端点处理
    [System.Serializable]
    public class ApiResponse
    {
        public bool success;
        public string message;
    }

    public ApiResponse HandleRequest(string endpoint, string method, string jsonData)
    {
        switch (endpoint.ToLower())
        {
            case "/status":
                return HandleStatus();
            case "/reset":
                return HandleReset(jsonData);
            case "/step":
                return HandleStep(jsonData);
            case "/valid_actions":
                return HandleValidActions();
            case "/render":
                return HandleRender();
            default:
                return new ApiResponse { success = false, message = "Unknown endpoint" };
        }
    }

    ApiResponse HandleStatus()
    {
        return new ApiResponse
        {
            success = true,
            message = "Unity Game Server Running",
            data = new
            {
                player_pos = player != null ? new { x = player.transform.position.x, y = player.transform.position.y } : null,
                boxes_count = boxes != null ? boxes.Count : 0,
                goals_count = goals != null ? goals.Count : 0,
                is_connected = true
            }
        };
    }

    ApiResponse HandleReset(string jsonData)
    {
        // 重置游戏逻辑
        if (player != null)
        {
            player.transform.position = Vector3.zero;
        }

        if (boxes != null)
        {
            foreach (var box in boxes)
            {
                box.transform.position = Vector3.zero;
            }
        }

        Debug.Log("[UnityGameServer] 游戏已重置");
        return new ApiResponse { success = true, message = "Game Reset" };
    }

    ApiResponse HandleStep(string jsonData)
    {
        // 解析动作
        // jsonData: {"action": "MOVE_FORWARD"}
        Debug.Log($"[UnityGameServer] 执行动作: {jsonData}");

        // 执行动作逻辑
        // 这里需要根据你的游戏具体实现

        return new ApiResponse { success = true, message = "Action Executed" };
    }

    ApiResponse HandleValidActions()
    {
        // 返回当前合法动作列表
        var actions = new List<string>
        {
            "MOVE_FORWARD",
            "MOVE_BACKWARD",
            "MOVE_LEFT",
            "MOVE_RIGHT",
            "JUMP",
            "ATTACK",
            "NONE"
        };

        return new ApiResponse
        {
            success = true,
            message = "Valid Actions",
            data = new { actions = actions }
        };
    }

    ApiResponse HandleRender()
    {
        // 返回屏幕截图（Base64 编码）
        // 这里需要实现屏幕截图功能
        return new ApiResponse
        {
            success = true,
            message = "Render Data",
            data = new { image = "" } // Base64 string
        };
    }
}
