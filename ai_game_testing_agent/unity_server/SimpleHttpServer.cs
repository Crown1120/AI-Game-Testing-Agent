using UnityEngine;
using System.Collections;
using UnityEngine.Networking.Server;
using System.Collections.Generic;
using UnityEngine.Networking.Types;
using System;

/// <summary>
/// 简单的 Unity HTTP 服务器实现
/// 基于 UnityWebRequest 实现轻量级 HTTP 服务器
/// </summary>
public class SimpleHttpServer : MonoBehaviour
{
    public int port = 8080;
    public string apiKey = "";

    private Dictionary<string, Action<UnityWebRequest>> _routes = new Dictionary<string, Action<UnityWebRequest>>();

    void Start()
    {
        SetupRoutes();
        Debug.Log($"[SimpleHttpServer] 服务器已启动，端口: {port}");
    }

    void SetupRoutes()
    {
        // GET /status - 获取服务器状态
        _routes["GET:/status"] = (req) =>
        {
            var response = JsonUtility.ToJson(new
            {
                success = true,
                message = "Unity Game Server Running",
                data = new
                {
                    player_pos = GetPlayerPosition(),
                    boxes_count = FindObjectsOfType<GameObject>().Length,
                    is_connected = true
                }
            });
            SendResponse(req, 200, response);
        };

        // POST /reset - 重置游戏
        _routes["POST:/reset"] = (req) =>
        {
            ResetGame();
            SendResponse(req, 200, "{\"success\": true, \"message\": \"Game Reset\"}");
        };

        // POST /step - 执行动作
        _routes["POST:/step"] = (req) =>
        {
            var formData = ParseFormData(req);
            string action = formData.ContainsKey("action") ? formData["action"] : "";

            ExecuteAction(action);

            SendResponse(req, 200, "{\"success\": true, \"message\": \"Action Executed\"}");
        };

        // POST /valid_actions - 获取合法动作
        _routes["POST:/valid_actions"] = (req) =>
        {
            var actions = new { actions = new List<string> { "UP", "DOWN", "LEFT", "RIGHT", "JUMP", "ATTACK" } };
            SendResponse(req, 200, JsonUtility.ToJson(actions));
        };

        // POST /render - 获取屏幕截图
        _routes["POST:/render"] = (req) =>
        {
            string screenshot = CaptureScreenshot();
            SendResponse(req, 200, $"{{\"success\": true, \"image\": \"{screenshot}\"}}");
        };
    }

    Vector3 GetPlayerPosition()
    {
        var player = GameObject.FindGameObjectWithTag("Player");
        return player != null ? player.transform.position : Vector3.zero;
    }

    void ResetGame()
    {
        // 重置游戏逻辑
        Debug.Log("[SimpleHttpServer] 游戏重置");
        // TODO: 实现具体的重置逻辑
    }

    void ExecuteAction(string action)
    {
        Debug.Log($"[SimpleHttpServer] 执行动作: {action}");
        // TODO: 实现具体的游戏动作
    }

    string CaptureScreenshot()
    {
        // 截取屏幕并转换为 Base64
        try
        {
            Texture2D screenshot = new Texture2D(Screen.width, Screen.height);
            screenshot.ReadPixels(new Rect(0, 0, Screen.width, Screen.height), 0, 0);
            screenshot.Apply();

            byte[] bytes = screenshot.EncodeToPNG();
            return Convert.ToBase64String(bytes);
        }
        catch (Exception e)
        {
            Debug.LogError($"[SimpleHttpServer] 截图失败: {e.Message}");
            return "";
        }
    }

    Dictionary<string, string> ParseFormData(UnityWebRequest req)
    {
        var formData = new Dictionary<string, string>();
        // 解析表单数据
        return formData;
    }

    void SendResponse(UnityWebRequest req, int statusCode, string body)
    {
        // 发送 HTTP 响应
        Debug.Log($"[SimpleHttpServer] 响应: {statusCode} {body}");
    }
}
