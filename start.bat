@echo off

REM ��������, ����������� �� ������� uv
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo ������� uv �� �������. ������������...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    if %errorlevel% neq 0 (
        echo ������ ��������� uv. ��������� ��������� Python � pip.
        exit /b 1
    )
) else (
    echo ������� uv ��� �����������.
)

echo.
echo �������� uv sync...
uv sync --link-mode=copy
if %errorlevel% neq 0 (
    echo ������ ��� ���������� uv sync.
    exit /b 1
)

echo.
echo �������� uv run main.py...
uv run main.py
