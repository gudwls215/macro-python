@echo off
echo 정밀 시간 동기화 매크로 시작...
echo.

set PYTHON_PATH=C:/dev/macro-python/.venv/Scripts/python.exe

echo 사용 가능한 옵션:
echo 1. 매크로 실행
echo 2. 예제 및 도구
echo 3. 테스트 서버 시작
echo.

set /p choice="선택하세요 (1-3): "

if "%choice%"=="1" (
    echo 매크로를 실행합니다...
    %PYTHON_PATH% time_sync_macro.py
) else if "%choice%"=="2" (
    echo 예제 및 도구를 실행합니다...
    %PYTHON_PATH% examples.py
) else if "%choice%"=="3" (
    echo 테스트 서버를 시작합니다...
    echo 브라우저에서 http://localhost:5000 을 열어 테스트하세요.
    %PYTHON_PATH% test_server.py
) else (
    echo 기본 매크로를 실행합니다...
    %PYTHON_PATH% time_sync_macro.py
)

pause
