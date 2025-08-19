@echo off
chcp 65001 > nul
title 최적화 빌드 - 정밀 구매 타이밍 매크로 v2.0

echo.
echo ==========================================
echo  최적화 빌드 시작 🚀
echo ==========================================
echo.

REM 이전 빌드 정리
echo 🧹 이전 빌드 정리 중...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM 최적화된 빌드
echo 🔨 최적화 빌드 시작...
pyinstaller ^
    --onefile ^
    --noconsole ^
    --name "PrecisionTimingMacro_v2.0" ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.messagebox ^
    --hidden-import=tkinter.scrolledtext ^
    --hidden-import=pyautogui ^
    --hidden-import=keyboard ^
    --hidden-import=pillow ^
    --hidden-import=PIL ^
    --hidden-import=winsound ^
    --exclude-module=selenium ^
    --exclude-module=webdriver_manager ^
    --exclude-module=matplotlib ^
    --exclude-module=numpy ^
    --exclude-module=scipy ^
    --exclude-module=pandas ^
    --version-file=version_info.txt ^
    --add-data="README.md;." ^
    --upx-dir="C:\Program Files\upx" ^
    gui_macro.py

REM 빌드 결과 확인
if exist "dist\PrecisionTimingMacro_v2.0.exe" (
    echo.
    echo ✅ 최적화 빌드 성공!
    
    REM 파일 정보 표시
    for %%A in ("dist\PrecisionTimingMacro_v2.0.exe") do (
        set size=%%~zA
        set /a size_mb=!size!/1024/1024
        echo 📊 파일 크기: !size_mb! MB
        echo 📅 생성 시간: %%~tA
    )
    
    echo.
    echo 📁 위치: %CD%\dist\PrecisionTimingMacro_v2.0.exe
    
    REM 실행 테스트
    echo.
    echo 🧪 실행 테스트를 하시겠습니까? (Y/N)
    choice /c YN /n
    if !errorlevel!==1 (
        echo 🎮 프로그램 테스트 실행 중...
        start "" "dist\PrecisionTimingMacro_v2.0.exe"
    )
    
    REM 폴더 열기
    echo.
    echo 📂 빌드 폴더를 열까요? (Y/N)
    choice /c YN /n
    if !errorlevel!==1 (
        start "" "dist\"
    )
    
) else (
    echo.
    echo ❌ 빌드 실패!
    echo 💡 build 폴더에서 로그를 확인하세요
    if exist "build" start "" "build"
)

echo.
echo 🎯 빌드 완료!
pause
