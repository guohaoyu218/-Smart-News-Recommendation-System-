@echo off
title News Recommendation System Launcher

echo =====================================
echo   News Recommendation System V2.0
echo ========================================
echo.

echo [1] ��װ������
echo [2] ������Ӧ�ã��Ƽ���
echo [3] ��������汾
echo [4] �������ݷ����Ǳ���
echo [5] �������ݷ�������
echo [6] ���к�̨�Ƽ�����
echo [7] �鿴ϵͳ״̬
echo [8] �˳�
echo.

set /p choice="��ѡ��Ҫִ�еĲ��� (1-8): "

if "%choice%"=="1" (
    echo.
    echo ���ڰ�װ������...
    pip install -r requirements.txt
    if %errorlevel%==0 (
        echo ��������װ�ɹ���
    ) else (
        echo ��������װʧ�ܣ������������Ӻ�Python������
    )
    pause
    goto menu
)

if "%choice%"=="2" (
    echo.
    echo �����������������Ƽ�ϵͳ��Ӧ��...
    echo ����������з���: http://localhost:8501
    echo.
    streamlit run app/app_main.py --server.port=8501
    goto end
)

if "%choice%"=="3" (
    echo.
    echo ������������汾...
    echo ����������з���: http://localhost:8502
    echo.
    streamlit run app/app_streamlit.py --server.port=8502
    goto end
)

if "%choice%"=="4" (
    echo.
    echo �����������ݷ����Ǳ���...
    echo ����������з���: http://localhost:8503
    echo.
    streamlit run app/dashboard.py --server.port=8503
    goto end
)

if "%choice%"=="5" (
    echo.
    echo �����������ݷ�������...
    echo ����������з���: http://localhost:8504
    echo.
    streamlit run app/content_analyzer.py --server.port=8504
    goto end
)

if "%choice%"=="6" (
    echo.
    echo ����������̨�Ƽ�����...
    python core/main.py
    pause
    goto menu
)

if "%choice%"=="7" (
    echo.
    echo ========================================
    echo              ϵͳ״̬���
    echo ========================================
    echo.
    
    echo ���Python����...
    python --version
    echo.
    
    echo ����Ѱ�װ�İ�...
    pip list | findstr "streamlit|pandas|numpy"
    echo.
    
    echo �����Ŀ�ļ�...
    if exist "core/main.py" (
        echo �� main.py ����
    ) else (
        echo �� main.py ������
    )
    
    if exist "app/app_main.py" (
        echo �� app_main.py ����
    ) else (
        echo �� app_main.py ������
    )
    
    if exist "requirements.txt" (
        echo �� requirements.txt ����
    ) else (
        echo �� requirements.txt ������
    )
    echo.
    
    echo ��������ļ�...
    if exist "MIND\MINDsmall_train\news.tsv" (
        echo �� ���������ļ�����
    ) else (
        echo �� ���������ļ�������
    )
    
    if exist "MIND\MINDsmall_train\behaviors.tsv" (
        echo �� �û���Ϊ�����ļ�����
    ) else (
        echo �� �û���Ϊ�����ļ�������
    )
    echo.
    
    echo ϵͳ״̬�����ɣ�
    pause
    goto menu
)

if "%choice%"=="8" (
    echo.
    echo ��лʹ�����������Ƽ�ϵͳ��
    goto end
)

echo ��Чѡ�����������롣
pause

:menu
cls
goto :eof

:end
pause
