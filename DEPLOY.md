# Cloudflare Pages 快速部署指南

## 最简单的方法：Direct Upload

1. **准备文件**
   确保你有以下文件在 `web` 目录中：
   - `index.html`
   - `styles.css`
   - `app.js`
   - `package.json`（可选）

2. **登录Cloudflare**
   访问 https://dash.cloudflare.com/ 并登录

3. **创建Pages项目**
   - 点击左侧菜单的 **Workers & Pages**
   - 点击 **Create application**
   - 选择 **Pages** 标签
   - 点击 **Upload assets**

4. **上传文件**
   - 输入项目名称（例如：facereplacer）
   - 点击 **Upload files**
   - 选择 `web` 目录下的所有文件
   - 点击 **Deploy site**

5. **完成！**
   等待几秒钟，你的网站就上线了！

## 通过Git部署（推荐用于持续更新）

### GitHub部署

1. **创建GitHub仓库**
   - 在GitHub上创建新仓库
   - 将 `web` 目录的内容推送到仓库

2. **连接Cloudflare**
   - 在Cloudflare Dashboard中进入 **Workers & Pages**
   - 点击 **Create application** → **Pages** → **Connect to Git**
   - 选择你的GitHub仓库
   - 点击 **Begin setup**

3. **配置构建设置**
   - 项目名称：facereplacer
   - 构建命令：留空
   - 构建输出目录：`web`（如果仓库根目录就是web内容，则留空）
   - 点击 **Save and Deploy**

### GitLab部署

步骤与GitHub类似，只需选择GitLab作为源即可。

## 使用Wrangler CLI部署

1. **安装Wrangler**
   ```bash
   npm install -g wrangler
   ```

2. **登录**
   ```bash
   wrangler login
   ```

3. **部署**
   ```bash
   cd web
   wrangler pages deploy . --project-name=facereplacer
   ```

## 域名配置（可选）

部署后，你可以：

1. **使用Cloudflare提供的域名**
   - 格式：`https://your-project.pages.dev`
   - 例如：`https://facereplacer.pages.dev`

2. **绑定自定义域名**
   - 在项目设置中点击 **Custom domains**
   - 点击 **Set up a custom domain**
   - 输入你的域名并按提示配置DNS

## 更新网站

### Direct Upload方式
每次更新需要重新上传所有文件

### Git方式
推送新代码到仓库，Cloudflare会自动部署

### Wrangler CLI
```bash
cd web
wrangler pages deploy . --project-name=facereplacer
```

## 常见问题

### Q: 部署后网站无法访问？
A: 检查文件是否正确上传，确保 `index.html` 在根目录

### Q: 如何查看部署日志？
A: 在项目页面点击 **Deployments** 查看部署历史和日志

### Q: 如何设置环境变量？
A: 在项目设置中点击 **Environment variables** 添加

### Q: 如何回滚到之前的版本？
A: 在 **Deployments** 页面找到之前的版本，点击 **Rollback**

## 性能优化建议

1. **图片优化**
   - 压缩上传的图片
   - 使用WebP格式

2. **缓存设置**
   - 在项目设置中配置缓存规则

3. **CDN**
   - Cloudflare Pages自动提供全球CDN加速

## 技术支持

- Cloudflare Pages文档：https://developers.cloudflare.com/pages/
- Wrangler CLI文档：https://developers.cloudflare.com/workers/wrangler/