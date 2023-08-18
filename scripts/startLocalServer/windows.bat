@echo off

:: Check argument count:
if "%1"=="" (
    echo No port specified
    exit /b 1
)

:: Start local server:
php -S localhost:%1 -t js\\src
