@echo off

where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing UV...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    if %errorlevel% neq 0 (
        echo Installing error
        exit /b 1
    )
    echo.
    set "Path=%USERPROFILE%\.local\bin;%Path%"
)

echo.
echo uv sync...
uv sync --link-mode=copy
if %errorlevel% neq 0 (
    echo uv sync error.
    exit /b 1
)

echo.
echo uv run main.py...
uv run main.py
