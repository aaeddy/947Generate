# FaceReplacer - 947

一个947生成器，可以替换图片中的眼睛和嘴巴。

## 功能特点

- 图片上传和预览
- 自定义预设图片（左眼、右眼、嘴巴）
- 拖拽调整元素位置
- 8个控制点调整元素大小
- 实时预览和保存结果
- 响应式设计，支持移动端
- 纯前端实现，无需后端

## 本地运行

### 方法1：使用Python（推荐）

```bash
cd web
python -m http.server 8080
```

然后在浏览器中打开 `http://localhost:8080`

### 方法2：使用Node.js

```bash
cd web
npm install
npm start
```

然后在浏览器中打开 `http://localhost:8080`

### 方法3：直接打开

直接在浏览器中打开 `index.html` 文件即可。

## 部署到Cloudflare Pages

### 方法1：通过Git仓库部署（推荐）

1. 将 `web` 目录推送到GitHub/GitLab仓库
2. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
3. 进入 **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**
4. 选择你的仓库并授权
5. 配置构建设置：
   - 构建命令：留空
   - 构建输出目录：`web`
6. 点击 **Save and Deploy**

### 方法2：通过Direct Upload部署

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 进入 **Workers & Pages** → **Create application** → **Pages** → **Upload assets**
3. 创建项目名称
4. 上传 `web` 目录下的所有文件：
   - `index.html`
   - `styles.css`
   - `app.js`
   - `package.json`
5. 点击 **Deploy site**

### 方法3：使用Wrangler CLI

1. 安装Wrangler CLI：
```bash
npm install -g wrangler
```

2. 登录Cloudflare：
```bash
wrangler login
```

3. 部署：
```bash
cd web
wrangler pages deploy . --project-name=facereplacer
```

## 使用说明

1. 点击"选择图片"上传要编辑的图片
2. 可选：上传预设的眼睛和嘴巴图片
3. 点击"开始处理"进入编辑模式
4. 拖动元素调整位置
5. 拖动8个控制点调整大小
6. 点击"保存结果"下载处理后的图片

### 快捷键

- `S` - 保存结果
- `R` - 重置元素位置
- `ESC` - 取消选择

## 文件结构

```
web/
├── index.html      # 主页面
├── styles.css      # 样式文件
├── app.js          # 核心逻辑
└── package.json    # 项目配置
```

## 技术栈

- HTML5 Canvas
- CSS3（响应式设计）
- 原生JavaScript（ES6+）
- 无外部依赖

## 浏览器兼容性

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+

## 注意事项

- 所有处理都在浏览器本地完成，图片不会上传到服务器
- 建议使用现代浏览器以获得最佳体验
- 大图片可能需要较长处理时间

## 许可证

MIT License