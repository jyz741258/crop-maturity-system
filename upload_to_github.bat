@echo off
echo ========================================
echo 叶用经济作物成熟度检测系统 - GitHub上传脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/6] 检查Git安装...
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git未安装，请先安装Git
    pause
    exit /b 1
)
echo ✅ Git已安装

echo.
echo [2/6] 初始化Git仓库...
if exist .git (
    echo Git仓库已存在
) else (
    git init
    echo ✅ Git仓库初始化成功
)

echo.
echo [3/6] 配置用户信息...
git config user.name "jyz741258"
git config user.email "jyz741258@users.noreply.github.com"
echo ✅ 用户信息已配置

echo.
echo [4/6] 添加文件...
git add .
echo ✅ 文件已添加

echo.
echo [5/6] 创建提交...
git commit -m "首次提交：叶用经济作物成熟度检测系统" 2>nul
if errorlevel 1 (
    echo ⚠️  可能是第一次提交或已有内容
) else (
    echo ✅ 提交成功
)

echo.
echo ========================================
echo 现在需要您在GitHub上创建仓库
echo.
echo 步骤：
echo 1. 访问: https://github.com/new
echo 2. 仓库名: crop-maturity-system
echo 3. 选择 Public 或 Private
echo 4. 不要勾选 README / .gitignore / License
echo 5. 点击 "Create repository"
echo ========================================
echo.

pause

set /p repo_url="请输入GitHub仓库地址（HTTPS）: "
echo.

echo [6/6] 关联远程仓库并推送...
git remote remove origin 2>nul
git remote add origin %repo_url%
git branch -M main
echo.
echo 正在推送到 GitHub...
echo.
echo 用户名: jyz741258
echo 密码: 使用Personal Access Token
echo.
git push -u origin main

echo.
echo ========================================
echo 上传完成！
echo 访问: %repo_url%
echo ========================================
pause
