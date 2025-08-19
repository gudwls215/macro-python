@echo off
chcp 65001 > nul
title 배포 패키지 생성 - 정밀 구매 타이밍 매크로 v2.0

echo.
echo ==========================================
echo  배포 패키지 생성 📦
echo ==========================================
echo.

REM 배포 폴더 생성
set release_name=PrecisionTimingMacro_v2.0_Release
echo 📁 배포 폴더 생성: %release_name%

if exist "%release_name%" rmdir /s /q "%release_name%"
mkdir "%release_name%"
mkdir "%release_name%\logs"
mkdir "%release_name%\docs"

REM 실행파일 복사
if exist "dist\PrecisionTimingMacro.exe" (
    echo 📋 실행파일 복사 중...
    copy "dist\PrecisionTimingMacro.exe" "%release_name%\"
) else (
    echo ❌ 실행파일이 없습니다! 먼저 빌드를 실행하세요.
    pause
    exit /b 1
)

REM 문서 파일들 복사
echo 📄 문서 파일 복사 중...
if exist "README.md" copy "README.md" "%release_name%\docs\"
if exist "INSTALL.md" copy "INSTALL.md" "%release_name%\docs\"
if exist "requirements.txt" copy "requirements.txt" "%release_name%\docs\"

REM 실행 배치 파일 생성
echo 🎮 실행 배치 파일 생성 중...
echo @echo off > "%release_name%\실행.bat"
echo title 정밀 구매 타이밍 매크로 v2.0 >> "%release_name%\실행.bat"
echo echo. >> "%release_name%\실행.bat"
echo echo ================^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^= >> "%release_name%\실행.bat"
echo echo  정밀 구매 타이밍 매크로 v2.0 🎯 >> "%release_name%\실행.bat"
echo echo ================^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^= >> "%release_name%\실행.bat"
echo echo. >> "%release_name%\실행.bat"
echo echo 🚀 프로그램을 시작합니다... >> "%release_name%\실행.bat"
echo echo 💡 관리자 권한으로 실행하면 더 정확한 결과를 얻을 수 있습니다 >> "%release_name%\실행.bat"
echo echo. >> "%release_name%\실행.bat"
echo start "" "PrecisionTimingMacro.exe" >> "%release_name%\실행.bat"

REM 관리자 권한 실행 배치 파일 생성
echo 🔧 관리자 권한 실행 파일 생성 중...
echo @echo off > "%release_name%\관리자권한실행.bat"
echo title 관리자 권한 실행 - 정밀 구매 타이밍 매크로 v2.0 >> "%release_name%\관리자권한실행.bat"
echo echo 🛡️ 관리자 권한으로 실행합니다... >> "%release_name%\관리자권한실행.bat"
echo powershell -Command "Start-Process 'PrecisionTimingMacro.exe' -Verb RunAs" >> "%release_name%\관리자권한실행.bat"

REM README 파일 생성
echo 📝 사용자 가이드 생성 중...
(
echo # 정밀 구매 타이밍 매크로 v2.0 - 실행 가이드
echo.
echo ## 🚀 빠른 시작
echo.
echo ### 1. 기본 실행
echo ```
echo 실행.bat 클릭 또는 PrecisionTimingMacro.exe 직접 실행
echo ```
echo.
echo ### 2. 관리자 권한 실행 ^(권장^)
echo ```
echo 관리자권한실행.bat 클릭
echo ```
echo.
echo ## 💡 사용법
echo.
echo 1. **URL 입력**: 구매할 웹사이트 주소
echo 2. **시간 동기화**: "시간 동기화 ^(5회^)" 클릭
echo 3. **좌표 설정**: "좌표 캡처 모드 ON" → Z키로 좌표 추가
echo 4. **목표 시간**: 원하는 시간 입력 ^(예: 15:30:00^)
echo 5. **매크로 시작**: "구매 매크로 시작" 클릭
echo.
echo ## 📁 폴더 구조
echo.
echo - `PrecisionTimingMacro.exe` - 메인 프로그램
echo - `실행.bat` - 간편 실행
echo - `관리자권한실행.bat` - 관리자 권한 실행
echo - `logs\` - 로그 파일 저장 폴더
echo - `docs\` - 문서 파일들
echo.
echo ## ⚠️ 주의사항
echo.
echo - Windows 10/11에서만 동작
echo - 안정적인 인터넷 연결 필요
echo - 웹사이트 이용약관 준수
echo - 교육/테스트 목적으로만 사용
echo.
echo ## 🔧 문제 해결
echo.
echo 1. **프로그램이 실행되지 않을 때**
echo    - 관리자 권한으로 실행
echo    - Windows Defender 예외 추가
echo.
echo 2. **클릭이 작동하지 않을 때**
echo    - 좌표 캡처 모드로 다시 설정
echo    - 관리자 권한으로 실행
echo.
echo 3. **시간 동기화 실패**
echo    - 네트워크 연결 확인
echo    - 방화벽 설정 확인
) > "%release_name%\사용법.txt"

REM 라이선스 파일 생성
echo ⚖️ 라이선스 파일 생성 중...
(
echo 정밀 구매 타이밍 매크로 v2.0 
echo Copyright ^(c^) 2025
echo.
echo 이 소프트웨어는 교육 및 테스트 목적으로만 제공됩니다.
echo.
echo 사용 조건:
echo 1. 웹사이트 이용약관을 준수해야 합니다
echo 2. 서버에 과도한 부하를 주지 않아야 합니다  
echo 3. 불법적인 용도로 사용할 수 없습니다
echo 4. 상업적 이용 시 별도 허가가 필요합니다
echo.
echo 면책 조항:
echo 본 소프트웨어 사용으로 인한 모든 결과에 대해 사용자가 책임집니다.
echo 개발자는 어떠한 손해에 대해서도 책임지지 않습니다.
) > "%release_name%\LICENSE.txt"

REM 패키지 정보 표시
echo.
echo ✅ 배포 패키지 생성 완료!
echo.
echo 📦 패키지 내용:
dir "%release_name%" /b

echo.
echo 📊 파일 크기:
for %%A in ("%release_name%\PrecisionTimingMacro.exe") do (
    set size=%%~zA
    set /a size_mb=!size!/1024/1024
    echo   실행파일: !size_mb! MB
)

echo.
echo 📁 패키지 위치: %CD%\%release_name%
echo.
echo 🎯 배포 준비 완료! 폴더를 열까요? ^(Y/N^)
choice /c YN /n
if !errorlevel!==1 (
    start "" "%release_name%"
)

pause
