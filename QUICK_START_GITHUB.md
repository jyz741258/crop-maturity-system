# GitHub 快速上传指南

## 📦 已准备的文件

✅ README.md - 项目说明文档  
✅ GITHUB_GUIDE.md - 详细上传指南  
✅ .gitignore - 已配置忽略文件  

## 🎯 快速开始（6步）

### 1️⃣ 打开命令行

在项目目录打开 PowerShell 或 CMD：
```
e:\中期报告\crop-maturity-system
```

### 2️⃣ 初始化 Git

```bash
git init
```

### 3️⃣ 配置你的信息

```bash
git config user.name "你的GitHub用户名"
git config user.email "你的邮箱"
```

### 4️⃣ 添加文件并提交

```bash
git add .
git commit -m "首次提交：叶用经济作物成熟度检测系统"
```

### 5️⃣ 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 输入仓库名（如：crop-maturity-system）
3. 选择 Public/Private
4. 不要勾选 README / .gitignore / License
5. 点击 "Create repository"

### 6️⃣ 推送代码

复制 GitHub 页面显示的 HTTPS 地址，执行：

```bash
git remote add origin https://github.com/你的用户名/仓库名.git
git branch -M main
git push -u origin main
```

## 🔐 登录提示

- 用户名：你的 GitHub 用户名
- 密码：使用 Personal Access Token（推荐）
  - 生成地址：https://github.com/settings/tokens
  - 权限：勾选 repo

## 📋 需要帮助？

查看详细指南：[GITHUB_GUIDE.md](GITHUB_GUIDE.md)
