using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;

/// <summary>
/// Unity 游戏 API 服务器 - HTTP 模式
///
/// 使用方法：
/// 1. 将此脚本添加到场景中的任意 GameObject
/// 2. 启动游戏后，API 服务器会在指定端口运行
/// 3. 从外部通过 HTTP 请求控制游戏
///
/// 支持的端点：
/// - GET  /status       - 获取服务器状态
/// - POST /reset        - 重置游戏
/// - POST /step         - 执行动作
/// - POST /valid_actions - 获取合法动作
/// - POST /render       - 获取屏幕截图
/// </summary>
public class UnityGameServer : MonoBehaviour
{
    // 配置
    public int port = 8080;

    // 使用 private + SerializeField 防止意外序列化暴露
    [SerializeField]
    private string apiKey = ""; // 留空表示不需要认证

    // 游戏状态
    private bool isGameRunning = true;
    private int currentSteps = 0;
    private float reward = 0f;

    // 动作空间
    public List<string> validActions = new List<string>
    {
        "MOVE_FORWARD", "MOVE_BACKWARD", "MOVE_LEFT", "MOVE_RIGHT",
        "LOOK_UP", "LOOK_DOWN", "LOOK_LEFT", "LOOK_RIGHT",
        "JUMP", "CROUCH", "ATTACK", "INTERACT", "NONE"
    };

    void Start()
    {
        StartCoroutine(StartServer());
        Debug.Log($"Unity Game Server started on port {port}");
    }

    IEnumerator StartServer()
    {
        // 使用 UnityWebRequest 创建简单的 HTTP 服务器
        // 注意：Unity 原生不支持 HTTP 服务器，这里使用第三方库或自定义协议
        // 本示例演示逻辑，实际部署需要使用 WebSocket 或 TCP

        Debug.Log("服务器启动中...");
        yield return null;
    }

    // 外部调用：重置游戏
    public void ResetGame(string levelId = null)
    {
        Debug.Log($"重置游戏，关卡: {levelId ?? "default"}");

        // 在这里添加你的重置逻辑
        // 例如：加载场景、重置玩家位置等

        currentSteps = 0;
        reward = 0f;
        isGameRunning = true;
    }

    // 外部调用：执行动作
    public void ExecuteAction(string action)
    {
        Debug.Log($"执行动作: {action}");

        // 根据动作类型执行相应逻辑
        switch (action)
        {
            case "MOVE_FORWARD":
                // 移动逻辑
                break;
            case "MOVE_BACKWARD":
                // 移动逻辑
                break;
            case "MOVE_LEFT":
                // 移动逻辑
                break;
            case "MOVE_RIGHT":
                // 移动逻辑
                break;
            case "JUMP":
                // 跳跃逻辑
                break;
            case "ATTACK":
                // 攻击逻辑
                break;
            case "INTERACT":
                // 交互逻辑
                break;
        }

        currentSteps++;
    }

    // 外部调用：获取合法动作
    public List<string> GetValidActions()
    {
        // 根据当前游戏状态返回合法动作
        // 例如：如果玩家在空中，不能跳跃
        return validActions;
    }

    // 外部调用：获取游戏状态
    public Dictionary<string, object> GetGameState()
    {
        return new Dictionary<string, object>
        {
            { "steps", currentSteps },
            { "is_running", isGameRunning },
            { "reward", reward }
        };
    }

    // 外部调用：获取屏幕截图
    public Texture2D GetScreenCapture()
    {
        // 确保渲染完成
        ScreenCapture.CaptureScreenshot("last_screenshot.png");
        Debug.Log("截图已保存");

        // 返回一个占位纹理
        return new Texture2D(2, 2);
    }

    // 编辑器模式下的测试方法
    [ContextMenu("Test Reset")]
    void TestReset()
    {
        ResetGame();
    }

    [ContextMenu("Test Action")]
    void TestAction()
    {
        ExecuteAction("MOVE_FORWARD");
    }
}
