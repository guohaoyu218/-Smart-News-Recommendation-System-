@echo off
title Git 初始化和上传助手
echo ========================================
echo      Git 初始化和上传助手
echo ========================================
echo.

echo 请选择要上传到的平台:
echo [1] GitHub
echo [2] Gitee (码云)
echo [3] 仅初始化本地 Git
echo [4] 退出
echo.

set /p choice="请选择 (1-4): "

if "%choice%"=="1" (
    set /p username="请输入你的 GitHub 用户名: "
    set /p reponame="请输入仓库名称 [默认: newsDP]: "
    if "!reponame!"=="" set reponame=newsDP
    set platform=github.com
    set remote_url=https://github.com/!username!/!reponame!.git
    goto setup_git
)

if "%choice%"=="2" (
    set /p username="请输入你的 Gitee 用户名: "
    set /p reponame="请输入仓库名称 [默认: newsDP]: "
    if "!reponame!"=="" set reponame=newsDP
    set platform=gitee.com
    set remote_url=https://gitee.com/!username!/!reponame!.git
    goto setup_git
)

if "%choice%"=="3" (
    goto local_only
)

if "%choice%"=="4" (
    exit
)

echo 无效选择，请重新运行。
pause
exit

:setup_git
echo.
echo 正在初始化 Git 仓库...
git init
if %errorlevel% neq 0 (
    echo Git 初始化失败，请确保已安装 Git
    pause
    exit
)

echo 正在添加文件...
git add .

echo 正在创建初始提交...
git commit -m "Initial commit: Smart News Recommendation System V2.0"

echo 正在设置远程仓库...
git remote add origin %remote_url%

echo 正在推送到远程仓库...
git branch -M main
git push -u origin main

if %errorlevel% eq 0 (
    echo.
    echo ========================================
    echo           上传成功！
    echo ========================================
    echo 仓库地址: %remote_url%
    echo.
    echo 注意事项:
    echo 1. .env 文件已被排除，不会上传敏感信息
    echo 2. 请在部署时创建 .env 文件并配置 API 密钥
    echo 3. 大型数据文件已被排除，需要单独处理
) else (
    echo.
    echo 上传失败，请检查:
    echo 1. 网络连接是否正常
    echo 2. 用户名和仓库名是否正确
    echo 3. 是否已在 %platform% 创建对应仓库
)

pause
exit

:local_only
echo.
echo 正在初始化本地 Git 仓库...
git init
git add .
git commit -m "Initial commit: Smart News Recommendation System V2.0"

echo.
echo 本地 Git 仓库初始化完成！
echo 后续可以手动添加远程仓库并推送。

pause
