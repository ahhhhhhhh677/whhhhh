# 部署到Render - 完整指南

## 准备工作

我已经为您创建了以下文件：
- ✅ `requirements.txt` - Python依赖
- ✅ `render.yaml` - Render服务配置
- ✅ 所有代码文件已准备就绪

## 部署步骤

### 第1步：创建GitHub仓库（2分钟）

1. 访问 https://github.com/new
2. 填写仓库信息：
   - Repository name: `ai-api-proxy`
   - Description: `AI API中转服务`
   - 选择 `Public`（公开）
   - 勾选 `Add a README file`
3. 点击 `Create repository`

### 第2步：上传代码到GitHub（3分钟）

在本地项目目录执行：

```bash
# 初始化git仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit"

# 连接远程仓库（替换YOUR_USERNAME为您的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/ai-api-proxy.git

# 推送代码
git push -u origin main
```

**或者使用GitHub Desktop**：
1. 下载 https://desktop.github.com/
2. 添加本地仓库
3. 推送到GitHub

### 第3步：在Render创建服务（3分钟）

1. 访问 https://dashboard.render.com
2. 点击 `New +` → `Web Service`
3. 选择GitHub授权，选择 `ai-api-proxy` 仓库
4. 配置服务：
   - **Name**: `ai-api-proxy`（或您喜欢的名字）
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app_proxy:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
5. 点击 `Advanced` 展开高级设置
6. 添加环境变量：
   - `SILICONFLOW_API_KEY` = `sk-olvfymjregzucoaqmgirgbsahiptcafpmdtenjumerlzvtem`
   - 其他配置保持不变
7. 点击 `Create Web Service`

### 第4步：等待部署完成（2分钟）

- Render会自动构建和部署
- 等待状态变为 `Live`
- 获得域名：`https://ai-api-proxy-xxx.onrender.com`

### 第5步：验证部署

1. 访问 `https://ai-api-proxy-xxx.onrender.com/health`
2. 应该返回：`{"status": "healthy"}`

## 部署后的配置

### 添加更多环境变量（可选）

在Render Dashboard → 您的服务 → Environment 中添加：

```
SILICONFLOW_API_KEY=sk-olvfymjregzucoaqmgirgbsahiptcafpmdtenjumerlzvtem
UPSTREAM_OPENAI_API_KEY=（如果有）
UPSTREAM_ANTHROPIC_API_KEY=（如果有）
```

### 自定义域名（可选）

1. 在Render Dashboard → Settings → Custom Domains
2. 添加您的域名
3. 按照提示配置DNS

## 营销内容更新

部署成功后，将营销内容中的地址更新为：

```
🚀 AI API中转服务正式上线！

✅ 访问地址：https://ai-api-proxy-xxx.onrender.com

（其他内容保持不变）
```

## 注意事项

### 免费版限制
- 15分钟无访问会休眠（首次访问需等待10-30秒唤醒）
- 每月750小时运行时间
- 512MB内存
- 足够初期使用

### 监控服务状态
- Render Dashboard会显示服务状态
- 可以设置告警

## 下一步

1. 完成上述部署步骤
2. 获得公网域名
3. 更新营销内容
4. 发布到GitHub、V2EX等平台
5. 开始获客！

---

**需要我协助您完成哪一步？**
