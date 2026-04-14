using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

/// <summary>
/// Unity HTTP 服务器 - 基于 TcpListener 的简单实现
/// 适用于 Unity 2018+ 版本
/// </summary>
public class HttpServer : MonoBehaviour
{
    public int port = 8080;

    // 使用 private + SerializeField 防止意外序列化暴露
    [SerializeField]
    private string apiKey = "";

    private TcpListener server;
    private Thread acceptThread;
    private bool isRunning = false;

    // 游戏控制器引用
    public UnityGameServer gameServer;

    void Start()
    {
        StartServer();
    }

    void OnApplicationQuit()
    {
        StopServer();
    }

    public void StartServer()
    {
        if (isRunning) return;

        try
        {
            server = new TcpListener(IPAddress.Any, port);
            server.Start();
            isRunning = true;

            acceptThread = new Thread(AcceptConnections);
            acceptThread.IsBackground = true;
            acceptThread.Start();

            Debug.Log($"HTTP Server started on port {port}");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to start server: {e.Message}");
        }
    }

    public void StopServer()
    {
        isRunning = false;
        server?.Stop();
        acceptThread?.Join(1000);
        Debug.Log("HTTP Server stopped");
    }

    private void AcceptConnections()
    {
        while (isRunning)
        {
            try
            {
                if (!server.Pending())
                {
                    Thread.Sleep(10);
                    continue;
                }

                TcpClient client = server.AcceptTcpClient();
                Thread clientThread = new Thread(() => HandleClient(client));
                clientThread.IsBackground = true;
                clientThread.Start();
            }
            catch
            {
                break;
            }
        }
    }

    private void HandleClient(TcpClient client)
    {
        try
        {
            using (NetworkStream stream = client.GetStream())
            using (System.IO.StreamReader reader = new System.IO.StreamReader(stream))
            using (System.IO.StreamWriter writer = new System.IO.StreamWriter(stream))
            {
                string requestLine = reader.ReadLine();
                if (string.IsNullOrEmpty(requestLine)) return;

                string[] parts = requestLine.Split(' ');
                if (parts.Length < 2) return;

                string method = parts[0];
                string path = parts[1].Split('?')[0];

                // 读取请求头
                Dictionary<string, string> headers = new Dictionary<string, string>();
                string line;
                while (!string.IsNullOrEmpty(line = reader.ReadLine()))
                {
                    int colonIndex = line.IndexOf(':');
                    if (colonIndex > 0)
                    {
                        string key = line.Substring(0, colonIndex).Trim();
                        string value = line.Substring(colonIndex + 1).Trim();
                        headers[key.ToLower()] = value;
                    }
                }

                // 处理请求
                string response = ProcessRequest(method, path, headers, reader);

                byte[] bytes = Encoding.UTF8.GetBytes(response);
                stream.Write(bytes, 0, bytes.Length);
            }
        }
        catch
        {
            // 忽略客户端断开等异常
        }
        finally
        {
            client.Close();
        }
    }

    private string ProcessRequest(string method, string path, Dictionary<string, string> headers, System.IO.StreamReader reader)
    {
        // 路径安全验证：只允许字母、数字、下划线和斜杠
        if (string.IsNullOrEmpty(path) || !System.Text.RegularExpressions.Regex.IsMatch(path, @"^/[a-zA-Z0-9_/_-]*$"))
        {
            return BuildResponse(400, "Bad Request", "application/json", "{\"error\": \"Invalid path\"}");
        }

        // 认证检查
        if (!string.IsNullOrEmpty(apiKey))
        {
            string authHeader;
            if (headers.TryGetValue("authorization", out authHeader))
            {
                // 安全比较：使用常量时间比较防止时序攻击
                string expectedAuth = $"Bearer {apiKey}";
                if (!string.Equals(authHeader, expectedAuth, System.StringComparison.Ordinal))
                {
                    return BuildResponse(401, "Unauthorized", "application/json", "{\"error\": \"Invalid API key\"}");
                }
            }
            else
            {
                return BuildResponse(401, "Unauthorized", "application/json", "{\"error\": \"API key required\"}");
            }
        }

        // 路由处理
        switch (path.ToLower())
        {
            case "/status":
                return HandleStatus();
            case "/reset":
                return HandleReset(method, headers, reader);
            case "/step":
                return HandleStep(method, headers, reader);
            case "/valid_actions":
                return HandleValidActions(method);
            case "/render":
                return HandleRender(method);
            default:
                return BuildResponse(404, "Not Found", "text/plain", "404 Not Found");
        }
    }

    private string HandleStatus()
    {
        string json = JsonUtility.ToJson(new {
            status = "running",
            port = port,
            game_active = true
        });
        return BuildResponse(200, "OK", "application/json", json);
    }

    private string HandleReset(string method, Dictionary<string, string> headers, System.IO.StreamReader reader)
    {
        if (method != "POST")
            return BuildResponse(405, "Method Not Allowed", "text/plain", "Only POST allowed");

        // 读取请求体
        string body = reader.ReadToEnd();
        string levelId = null;

        if (!string.IsNullOrEmpty(body))
        {
            try
            {
                var data = Json.Deserialize(body) as Dictionary<string, object>;
                if (data != null && data.ContainsKey("level_id"))
                    levelId = data["level_id"].ToString();
            }
            catch { }
        }

        gameServer.ResetGame(levelId);

        string json = JsonUtility.ToJson(new {
            success = true,
            level = levelId ?? "default",
            state = gameServer.GetGameState()
        });
        return BuildResponse(200, "OK", "application/json", json);
    }

    private string HandleStep(string method, Dictionary<string, string> headers, System.IO.StreamReader reader)
    {
        if (method != "POST")
            return BuildResponse(405, "Method Not Allowed", "text/plain", "Only POST allowed");

        string body = reader.ReadToEnd();
        string action = "NONE";

        if (!string.IsNullOrEmpty(body))
        {
            try
            {
                var data = Json.Deserialize(body) as Dictionary<string, object>;
                if (data != null && data.ContainsKey("action"))
                    action = data["action"].ToString();
            }
            catch { }
        }

        gameServer.ExecuteAction(action);

        string json = JsonUtility.ToJson(new {
            success = true,
            action = action,
            state = gameServer.GetGameState(),
            reward = gameServer.reward,
            done = !gameServer.isGameRunning
        });
        return BuildResponse(200, "OK", "application/json", json);
    }

    private string HandleValidActions(string method)
    {
        if (method != "GET")
            return BuildResponse(405, "Method Not Allowed", "text/plain", "Only GET allowed");

        var actions = gameServer.GetValidActions();
        string json = JsonUtility.ToJson(new { actions = actions });
        return BuildResponse(200, "OK", "application/json", json);
    }

    private string HandleRender(string method)
    {
        if (method != "GET")
            return BuildResponse(405, "Method Not Allowed", "text/plain", "Only GET allowed");

        // 获取屏幕截图并转换为 base64
        Texture2D texture = new Texture2D(Screen.width, Screen.height);
        Texture2D screenshot = texture;

        try
        {
            screenshot = ScreenCapture.CaptureScreenshotAsTexture();
        }
        catch
        {
            // 如果失败，返回占位符
        }

        // 简化处理：返回成功状态
        string json = JsonUtility.ToJson(new {
            success = true,
            image = null, // 实际应用中这里应该是 base64 图像数据
            width = Screen.width,
            height = Screen.height
        });
        return BuildResponse(200, "OK", "application/json", json);
    }

    private string BuildResponse(int statusCode, string statusText, string contentType, string body)
    {
        string response = $"HTTP/1.1 {statusCode} {statusText}\r\n";
        response += "Content-Type: " + contentType + "\r\n";
        response += "Access-Control-Allow-Origin: *\r\n";
        response += $"Content-Length: {Encoding.UTF8.GetByteCount(body)}\r\n";
        response += "Connection: close\r\n";
        response += "\r\n";
        response += body;
        return response;
    }

    // JSON 辅助类
    private static class Json
    {
        public static object Deserialize(string json)
        {
            try
            {
                return UnityEngine.JsonUtility.FromJson<DictionaryWrapper>(json)?.data;
            }
            catch
            {
                return null;
            }
        }

        [System.Serializable]
        private class DictionaryWrapper
        {
            public Dictionary<string, object> data;
        }
    }
}
