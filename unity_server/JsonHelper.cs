using UnityEngine;

/// <summary>
/// 简单的 JSON 序列化辅助类
/// </summary>
public static class JsonHelper
{
    /// <summary>
    /// 将对象序列化为 JSON 字符串
    /// </summary>
    public static string ToJson<T>(T obj)
    {
        return JsonUtility.ToJson(obj, true);
    }

    /// <summary>
    /// 从 JSON 字符串反序列化对象
    /// </summary>
    public static T FromJson<T>(string json)
    {
        return JsonUtility.FromJson<T>(json);
    }

    /// <summary>
    /// 将对象序列化为 JSON 字符串（支持字典）
    /// </summary>
    public static string SerializeObject(object obj)
    {
        try
        {
            return MiniJson.Serialize(obj);
        }
        catch
        {
            return "{}";
        }
    }

    /// <summary>
    /// 从 JSON 字符串反序列化为字典
    /// </summary>
    public static Dictionary<string, object> DeserializeObject(string json)
    {
        try
        {
            var result = MiniJson.Deserialize(json) as Dictionary<string, object>;
            return result ?? new Dictionary<string, object>();
        }
        catch
        {
            return new Dictionary<string, object>();
        }
    }
}

/// <summary>
/// 简易 JSON 解析器（无需依赖全功能 JSON 库）
/// </summary>
public static class MiniJson
{
    public static object Deserialize(string json)
    {
        if (string.IsNullOrEmpty(json))
            return null;

        var trimmed = json.Trim();
        if (trimmed.StartsWith("{"))
            return ParseObject(json);
        else if (trimmed.StartsWith("["))
            return ParseArray(json);
        else
            return ParseValue(json);
    }

    public static string Serialize(object obj)
    {
        if (obj == null)
            return "null";

        if (obj is bool)
            return ((bool)obj) ? "true" : "false";

        if (obj is string)
            return "\"" + EscapeString((string)obj) + "\"";

        if (obj is float || obj is double || obj is int || obj is long || obj is decimal)
            return obj.ToString();

        if (obj is System.Collections.IDictionary)
            return SerializeDictionary((System.Collections.IDictionary)obj);

        if (obj is System.Collections.IEnumerable)
            return SerializeEnumerable((System.Collections.IEnumerable)obj);

        return SerializeObjectProperties(obj);
    }

    private static object ParseObject(string json)
    {
        var result = new System.Collections.Hashtable();
        var inner = json.Trim().Substring(1, json.Length - 2).Trim();

        if (string.IsNullOrEmpty(inner))
            return result;

        var pairs = ParsePairs(inner);
        foreach (DictionaryEntry pair in pairs)
        {
            result[pair.Key.ToString()] = pair.Value;
        }

        return result;
    }

    private static object ParseArray(string json)
    {
        var inner = json.Trim().Substring(1, json.Length - 2).Trim();

        if (string.IsNullOrEmpty(inner))
            return new object[0];

        var result = new System.Collections.ArrayList();
        var values = ParseArrayValues(inner);

        foreach (var value in values)
        {
            result.Add(value);
        }

        return result.ToArray();
    }

    private static object ParseValue(string json)
    {
        var trimmed = json.Trim();

        if (trimmed == "null")
            return null;

        if (trimmed == "true")
            return true;

        if (trimmed == "false")
            return false;

        if (trimmed.StartsWith("\""))
            return ParseString(trimmed);

        if (float.TryParse(trimmed, out float f))
            return f;

        return null;
    }

    private static string ParseString(string json)
    {
        if (json.Length < 2 || !json.StartsWith("\"") || !json.EndsWith("\""))
            return json;

        return json.Substring(1, json.Length - 2);
    }

    private static System.Collections.IDictionary ParsePairs(string json)
    {
        var result = new System.Collections.Hashtable();
        int i = 0;
        int len = json.Length;

        while (i < len)
        {
            // 跳过空白
            while (i < len && char.IsWhiteSpace(json[i])) i++;

            if (i >= len) break;

            // 读取键
            if (json[i] != '"') break;
            string key = ParseString(json.Substring(i));
            i += key.Length + 2;

            // 跳过冒号和空白
            while (i < len && (json[i] == ':' || char.IsWhiteSpace(json[i]))) i++;

            // 读取值
            object value;
            if (json[i] == '"')
            {
                value = ParseString(json.Substring(i));
                i += value.ToString().Length + 2;
            }
            else if (json[i] == '{')
            {
                int braceCount = 1;
                int start = i;
                i++;
                while (i < len && braceCount > 0)
                {
                    if (json[i] == '{') braceCount++;
                    else if (json[i] == '}') braceCount--;
                    i++;
                }
                value = ParseObject(json.Substring(start, i - start));
            }
            else
            {
                string valueStr = "";
                while (i < len && json[i] != ',' && json[i] != '}' && !char.IsWhiteSpace(json[i]))
                {
                    valueStr += json[i];
                    i++;
                }
                value = ParseValue(valueStr);
            }

            result[key] = value;
            i++;

            // 跳过逗号和空白
            while (i < len && (json[i] == ',' || char.IsWhiteSpace(json[i]))) i++;
        }

        return result;
    }

    private static System.Collections.IList ParseArrayValues(string json)
    {
        var result = new System.Collections.ArrayList();
        int i = 0;
        int len = json.Length;

        while (i < len)
        {
            while (i < len && char.IsWhiteSpace(json[i])) i++;

            if (i >= len) break;

            object value;
            if (json[i] == '"')
            {
                value = ParseString(json.Substring(i));
                i += value.ToString().Length + 2;
            }
            else if (json[i] == '{')
            {
                int braceCount = 1;
                int start = i;
                i++;
                while (i < len && braceCount > 0)
                {
                    if (json[i] == '{') braceCount++;
                    else if (json[i] == '}') braceCount--;
                    i++;
                }
                value = ParseObject(json.Substring(start, i - start));
            }
            else
            {
                string valueStr = "";
                while (i < len && json[i] != ',' && json[i] != ']' && !char.IsWhiteSpace(json[i]))
                {
                    valueStr += json[i];
                    i++;
                }
                value = ParseValue(valueStr);
            }

            result.Add(value);
            i++;

            while (i < len && (json[i] == ',' || char.IsWhiteSpace(json[i]))) i++;
        }

        return result;
    }

    private static string EscapeString(string s)
    {
        return s.Replace("\\", "\\\\").Replace("\"", "\\\"");
    }

    private static string SerializeDictionary(System.Collections.IDictionary dict)
    {
        var entries = new System.Collections.ArrayList();
        foreach (DictionaryEntry entry in dict)
        {
            string key = "\"" + EscapeString(entry.Key.ToString()) + "\"";
            string value = Serialize(entry.Value);
            entries.Add(key + ":" + value);
        }
        return "{" + string.Join(",", (string[])entries.ToArray(typeof(string))) + "}";
    }

    private static string SerializeEnumerable(System.Collections.IEnumerable enumerable)
    {
        var entries = new System.Collections.ArrayList();
        foreach (var item in enumerable)
        {
            entries.Add(Serialize(item));
        }
        return "[" + string.Join(",", (string[])entries.ToArray(typeof(string))) + "]";
    }

    private static string SerializeObjectProperties(object obj)
    {
        var type = obj.GetType();
        var entries = new System.Collections.ArrayList();

        foreach (var prop in type.GetProperties())
        {
            try
            {
                var value = prop.GetValue(obj, null);
                string key = "\"" + prop.Name + "\"";
                string valueStr = Serialize(value);
                entries.Add(key + ":" + valueStr);
            }
            catch
            {
                // 跳过无法访问的属性
            }
        }

        foreach (var field in type.GetFields())
        {
            try
            {
                object value = field.GetValue(obj);
                string key = "\"" + field.Name + "\"";
                string valueStr = Serialize(value);
                entries.Add(key + ":" + valueStr);
            }
            catch
            {
                // 跳过无法访问的字段
            }
        }

        return "{" + string.Join(",", (string[])entries.ToArray(typeof(string))) + "}";
    }
}
