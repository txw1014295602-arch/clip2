
# 📺 电视剧剪辑系统 - 详细使用教程

## 🚀 一键快速开始

### 方法1：使用主程序（推荐）
1. 点击右上角的 **Run** 按钮
2. 选择对应的功能选项
3. 按提示操作即可

### 方法2：直接运行分析
在Console中输入：
```bash
python3 main.py
```

## 📋 完整使用流程

### 第一步：准备字幕文件
确保您的字幕文件已经上传到项目根目录，格式如：
- `S01E01_4K_60fps.txt`
- `S01E02_4K_60fps.txt`
- ...

**字幕文件格式要求：**
```
1
00:00:15,230 --> 00:00:18,660
我要为四二八案申请重审

2
00:00:19,440 --> 00:00:22,320
这个证据证明当年的判决有误
```

### 第二步：选择分析模式

#### 🔥 一键剪辑（最简单）
1. 点击 **Run** 按钮
2. 选择 `1. 📝 仅进行字幕分析`
3. 等待分析完成，查看生成的 `professional_editing_plan.txt`

#### 🎬 完整视频剪辑
1. 创建 `videos/` 文件夹
2. 上传对应的视频文件（如 `S01E01_4K_60fps.mp4`）
3. 选择 `2. 🎬 完整剪辑流程`

## 🤖 AI接口配置详细教程

### 快速配置AI增强
1. 运行主程序：`python3 main.py`
2. 选择 `3. 🤖 配置AI增强分析`
3. 按以下步骤配置：

### 支持的AI服务商配置

#### 1. OpenAI (ChatGPT)
```
选择：1. OpenAI
模型选择：1 (gpt-3.5-turbo) 或 2 (gpt-4)
API密钥：sk-xxxxxxxxxxxxxxxx (从 https://platform.openai.com/api-keys 获取)
```

#### 2. DeepSeek（推荐，性价比高）
```
选择：2. DeepSeek
模型选择：1 (deepseek-chat)
API密钥：sk-xxxxxxxxxxxxxxxx (从 https://platform.deepseek.com 获取)
```

#### 3. Moonshot (Kimi)
```
选择：3. Moonshot
模型选择：1 (moonshot-v1-8k)
API密钥：sk-xxxxxxxxxxxxxxxx (从 https://platform.moonshot.cn 获取)
```

#### 4. 通义千问
```
选择：4. 通义千问
模型选择：1 (qwen-turbo)
API密钥：sk-xxxxxxxxxxxxxxxx (从阿里云DashScope获取)
```

#### 5. 智谱清言 (GLM)
```
选择：5. 智谱清言
模型选择：1 (glm-4)
API密钥：xxxxxxxxxxxxxxxx (从 https://open.bigmodel.cn 获取)
```

#### 6. 自定义API接口
```
选择：7. 自定义API接口
API地址：https://your-api-endpoint.com/v1/chat/completions
API密钥：your-api-key
模型名称：your-model-name
```

### API密钥获取方法

#### OpenAI API密钥获取
1. 访问 https://platform.openai.com/api-keys
2. 点击 "Create new secret key"
3. 复制生成的密钥（sk-开头）

#### DeepSeek API密钥获取
1. 访问 https://platform.deepseek.com
2. 注册并登录账户
3. 进入API管理页面
4. 创建新的API密钥

#### Moonshot (Kimi) API密钥获取
1. 访问 https://platform.moonshot.cn
2. 注册并实名认证
3. 进入控制台创建API密钥

### 🔧 通过Replit Secrets配置（更安全）

推荐使用Replit的Secrets功能存储API密钥：

1. 点击左侧工具栏的 **Tools** → **Secrets**
2. 点击 **+ New Secret**
3. 添加以下密钥：

```
Secret Key: AI_API_KEY
Value: 您的API密钥

Secret Key: AI_API_PROVIDER  
Value: openai (或 deepseek, kimi 等)

Secret Key: AI_MODEL
Value: gpt-3.5-turbo (或其他模型)
```

## 📊 使用示例

### 示例1：纯字幕分析
```bash
# 运行主程序
python3 main.py

# 选择选项
选择: 1

# 输出结果
✅ 分析完成！
📊 成功分析了 15 集
📄 详细方案已保存到: professional_editing_plan.txt
```

### 示例2：AI增强分析
```bash
# 配置AI
python3 main.py
选择: 3  # 配置AI
选择: 2  # DeepSeek
输入API密钥: sk-your-key-here
选择分析模式: 2  # 混合模式

# 开始分析
选择: 1  # 字幕分析
```

### 示例3：完整视频剪辑
```bash
# 确保视频文件已上传到videos/文件夹
# 运行完整流程
python3 main.py
选择: 2  # 完整剪辑流程

# 输出结果
🎉 剪辑完成！
✅ 成功剪辑了 15 集
📁 视频文件保存在: professional_clips/
```

## 📁 输出文件说明

### 分析报告
- `professional_editing_plan.txt`: 详细剪辑方案
- 包含每集的时间码、剧情分析、衔接说明

### 视频文件（如果进行了剪辑）
- `professional_clips/E01_主题.mp4`: 单集精彩片段
- `professional_clips/Complete_Series_Professional_Highlights.mp4`: 完整合集

## 🔍 常见问题解决

### Q1: 提示"找不到字幕文件"
**解决方案：**
- 确保字幕文件命名格式为：`S01E01_4K_60fps.txt`
- 文件需要放在项目根目录
- 检查文件编码是否为UTF-8

### Q2: AI分析不工作
**解决方案：**
```bash
# 检查配置
python3 main.py
选择: 4  # 查看系统状态

# 重新配置API
选择: 3  # 配置AI
```

### Q3: 视频剪辑失败
**解决方案：**
- 确保视频文件在 `videos/` 文件夹中
- 视频文件名需要与字幕文件名匹配
- 检查视频格式是否支持（推荐mp4）

### Q4: 分析结果为空
**解决方案：**
- 检查字幕内容是否包含相关关键词
- 可以在 `subtitle_analyzer.py` 中调低分数阈值
- 确认字幕格式正确

## ⚡ 高级技巧

### 批量处理技巧
```bash
# 一次性分析所有集数
python3 subtitle_analyzer.py

# 一次性剪辑所有视频
python3 video_clipper.py
```

### 自定义关键词
在 `subtitle_analyzer.py` 中添加特定关键词：
```python
# 找到这行代码并修改
self.main_plot_keywords.extend(['您的关键词1', '关键词2'])
```

### 调整剪辑时长
```python
# 在 subtitle_analyzer.py 中修改
if 120 <= duration <= 180:  # 改为您想要的时长范围（秒）
```

## 🎯 最佳实践

1. **首次使用**：先进行字幕分析，检查结果质量
2. **AI增强**：建议使用混合模式，平衡准确性和效率
3. **视频剪辑**：确保有足够磁盘空间（每集约100-200MB）
4. **批量处理**：大量文件时建议分批处理

## 💡 提示

- 系统会自动修正常见错别字
- 支持多种视频格式（mp4, mkv, avi等）
- 生成的方案可以手动调整后再剪辑
- 所有配置都会自动保存，下次使用时无需重新配置

有任何问题欢迎随时咨询！
