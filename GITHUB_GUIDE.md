# GitHub上传指南

## 📋 前提条件

1. 已安装 Git
2. 已有 GitHub 账户
3. 已在 GitHub 上创建仓库

## 🚀 上传步骤

### 步骤1: 初始化 Git 仓库

```bash
# 进入项目目录
cd e:\中期报告\crop-maturity-system

# 初始化 Git 仓库
git init
```

### 步骤2: 配置用户信息

```bash
git config user.name "你的用户名"
git config user.email "你的邮箱@example.com"
```

### 步骤3: 添加文件到暂存区

```bash
git add .
```

### 步骤4: 创建首次提交

```bash
git commit -m "首次提交：叶用经济作物成熟度检测系统"
```

### 步骤5: 关联远程仓库

```bash
# 替换为你的仓库地址
git remote add origin https://github.com/你的用户名/仓库名.git
```

### 步骤6: 推送到 GitHub

```bash
# 首次推送
git branch -M main
git push -u origin main
```

## 🔐 使用个人访问令牌（推荐）

如果提示输入密码，请使用 GitHub 个人访问令牌（Personal Access Token）。

创建令牌步骤：
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token"
3. 选择 `repo` 权限
4. 复制生成的令牌（只显示一次！）
5. 用此令牌替代密码登录

## 📌 后续更新

```bash
# 查看状态
git status

# 添加修改
git add .

# 提交
git commit -m "更新说明"

# 推送
git push
```

## ⚠️ 重要提示

- 不要上传：
  - 大型数据集（crop-image/已在.gitignore中）
  - 训练模型文件（models/*.pth, *.pkl）
  - 敏感信息（密钥、密码等）
