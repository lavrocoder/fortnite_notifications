@echo off

REM Проверка, установлена ли утилита uv
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo Утилита uv не найдена. Устанавливаю...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    if %errorlevel% neq 0 (
        echo Ошибка установки uv. Проверьте установку Python и pip.
        exit /b 1
    )
) else (
    echo Утилита uv уже установлена.
)

echo.
echo Выполняю uv sync...
uv sync --link-mode=copy
if %errorlevel% neq 0 (
    echo Ошибка при выполнении uv sync.
    exit /b 1
)

echo.
echo Запускаю uv run main.py...
uv run main.py
