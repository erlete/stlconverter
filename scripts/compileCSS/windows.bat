@echo off

:: Check argument count:
if "%1"=="" (
    echo No compilation mode specified
    exit /b 1
)

:: Check argument values:
if "%1"=="Single" (
    set extraArg=
) else if "%1"=="Continuous" (
    set extraArg=-w
) else (
    echo Invalid compilation mode specified
    exit /b 1
)

:: Compile CSS:
cd js
npx tailwindcss -i src\\styles\\template.css -o src\\styles\\output.css %extraArg%
