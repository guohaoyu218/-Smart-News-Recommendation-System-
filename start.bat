@echo off
title News Recommendation System Launcher

echo =====================================
echo   News Recommendation System V2.0
echo ========================================
echo.

echo [1] 安装依赖包
echo [2] 启动主应用（推荐）
echo [3] 启动经典版本
echo [4] 启动数据分析仪表板
echo [5] 启动内容分析工具
echo [6] 运行后台推荐服务
echo [7] 查看系统状态
echo [8] 退出
echo.

set /p choice="请选择要执行的操作 (1-8): "

if "%choice%"=="1" (
    echo.
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if %errorlevel%==0 (
        echo 依赖包安装成功！
    ) else (
        echo 依赖包安装失败，请检查网络连接和Python环境。
    )
    pause
    goto menu
)

if "%choice%"=="2" (
    echo.
    echo 正在启动智能新闻推荐系统主应用...
    echo 请在浏览器中访问: http://localhost:8501
    echo.
    streamlit run app_main.py --server.port=8501
    goto end
)

if "%choice%"=="3" (
    echo.
    echo 正在启动经典版本...
    echo 请在浏览器中访问: http://localhost:8502
    echo.
    streamlit run app_streamlit.py --server.port=8502
    goto end
)

if "%choice%"=="4" (
    echo.
    echo 正在启动数据分析仪表板...
    echo 请在浏览器中访问: http://localhost:8503
    echo.
    streamlit run dashboard.py --server.port=8503
    goto end
)

if "%choice%"=="5" (
    echo.
    echo 正在启动内容分析工具...
    echo 请在浏览器中访问: http://localhost:8504
    echo.
    streamlit run content_analyzer.py --server.port=8504
    goto end
)

if "%choice%"=="6" (
    echo.
    echo 正在启动后台推荐服务...
    python main.py
    pause
    goto menu
)

if "%choice%"=="7" (
    echo.
    echo ========================================
    echo              系统状态检查
    echo ========================================
    echo.
    
    echo 检查Python环境...
    python --version
    echo.
    
    echo 检查已安装的包...
    pip list | findstr "streamlit|pandas|numpy"
    echo.
    
    echo 检查项目文件...
    if exist "main.py" (
        echo √ main.py 存在
    ) else (
        echo × main.py 不存在
    )
    
    if exist "app_main.py" (
        echo √ app_main.py 存在
    ) else (
        echo × app_main.py 不存在
    )
    
    if exist "requirements.txt" (
        echo √ requirements.txt 存在
    ) else (
        echo × requirements.txt 不存在
    )
    echo.
    
    echo 检查数据文件...
    if exist "MIND\MINDsmall_train\news.tsv" (
        echo √ 新闻数据文件存在
    ) else (
        echo × 新闻数据文件不存在
    )
    
    if exist "MIND\MINDsmall_train\behaviors.tsv" (
        echo √ 用户行为数据文件存在
    ) else (
        echo × 用户行为数据文件不存在
    )
    echo.
    
    echo 系统状态检查完成！
    pause
    goto menu
)

if "%choice%"=="8" (
    echo.
    echo 感谢使用智能新闻推荐系统！
    goto end
)

echo 无效选择，请重新输入。
pause

:menu
cls
goto :eof

:end
pause
