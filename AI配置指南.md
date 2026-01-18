
# 🤖 AI配置指南

## 快速配置

创建 `.ai_config.json` 文件，内容如下：

### OpenAI官方API
```json
{
    "enabled": true,
    "provider": "openai",
    "api_key": "your-openai-api-key",
    "model": "gpt-3.5-turbo",
    "base_url": "https://api.openai.com/v1"
}
```

### 中转API示例
```json
{
    "enabled": true,
    "provider": "proxy",
    "api_key": "your-proxy-api-key",
    "model": "gpt-3.5-turbo",
    "base_url": "https://your-proxy-url.com/v1"
}
```

### DeepSeek API
```json
{
    "enabled": true,
    "provider": "deepseek",
    "api_key": "your-deepseek-api-key",
    "model": "deepseek-chat",
    "base_url": "https://api.deepseek.com/v1"
}
```

## 使用说明

1. 将上述配置保存为项目根目录下的 `.ai_config.json` 文件
2. 替换 `your-api-key` 为实际的API密钥
3. 如使用中转API，替换 `base_url` 为实际地址
4. 运行系统即可开始AI分析

## 注意事项

- 本系统100%依赖AI分析，必须配置AI才能运行
- API调用可能产生费用，请注意使用量
- 建议使用支持长文本的模型以获得最佳效果
