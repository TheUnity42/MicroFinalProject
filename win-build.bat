@echo off

WHERE python.exe >nul 2>&1 || ( echo Python is not installed. Please install Python 3.x and try again. && exit /b )
WHERE npm >nul 2>&1 || ( echo npm is not installed. Please install npm and try again. && exit /b )
WHERE node.exe >nul 2>&1 || ( echo node.exe is not installed. Please install NodeJS and try again. && exit /b )

IF [%1]==[] (
    echo "Defauling to dev build"
    SET DEBUG=1
) ELSE (
    if [%1]==[--debug] (
        SET DEBUG=1
    ) ELSE (
        SET DEBUG=0
    )
)

CD "EffectsModule"
RMDIR /S /Q "build"

IF NOT EXIST "resources" (
    mkdir "resources"
    CALL tar -xzvf ../Resources-x64.tar.gz
)

CALL npm install
IF [DEBUG]==1 (
    CALL npm run build-debug
) ELSE (
    CALL npm run build-release
)

CD "../ElectronGUI"
CALL npm install

IF [DEBUG]==1 (
    goto exit
) ELSE (
    CALL npm run build
)

:exit
CD ".."
