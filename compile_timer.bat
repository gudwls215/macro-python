@echo off
echo C++ 정밀 타이머 컴파일 중...

:: Visual Studio Build Tools 찾기
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" (
    call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64
) else if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
) else if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat" (
    call "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat" x64
) else (
    echo Visual Studio가 설치되지 않아 C++ 컴파일러를 찾을 수 없습니다.
    echo MinGW-w64로 컴파일을 시도합니다...
    
    :: MinGW-w64 시도
    where g++ >nul 2>nul
    if errorlevel 1 (
        echo g++ 컴파일러를 찾을 수 없습니다.
        echo 다음 중 하나를 설치하세요:
        echo 1. Visual Studio 2022 Community (무료)
        echo 2. MinGW-w64
        pause
        exit /b 1
    ) else (
        echo MinGW-w64로 컴파일 중...
        g++ -std=c++11 -O2 -o precision_timer.exe precision_timer.cpp -lwinmm
        if errorlevel 0 (
            echo 컴파일 성공: precision_timer.exe
        ) else (
            echo 컴파일 실패!
        )
    )
    goto :end
)

:: Visual Studio 컴파일러 사용
echo Visual Studio 컴파일러로 컴파일 중...
cl /O2 /EHsc precision_timer.cpp /link winmm.lib /out:precision_timer.exe

if exist precision_timer.exe (
    echo 컴파일 성공: precision_timer.exe
    echo.
    echo 테스트 실행 중...
    precision_timer.exe 1000000
) else (
    echo 컴파일 실패!
)

:end
pause
