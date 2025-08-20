@echo off
:: Local development setup script for Insurance Claim Orchestrator (Windows)

echo 🚀 Setting up Insurance Claim Orchestrator for local development...

:: Check Python version
echo 🐍 Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.9+ first.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✅ Python found: %python_version%

:: Check if Functions Core Tools is installed
echo ⚡ Checking Azure Functions Core Tools...
func --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Azure Functions Core Tools not found. Please install it first:
    echo    npm install -g azure-functions-core-tools@4 --unsafe-perm true
    pause
    exit /b 1
)

for /f %%i in ('func --version 2^>^&1') do set func_version=%%i
echo ✅ Functions Core Tools installed: %func_version%

:: Create virtual environment
echo 🌍 Creating Python virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

:: Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

:: Check if local.settings.json exists
echo ⚙️ Checking configuration...
if not exist "local.settings.json" (
    echo ⚠️ local.settings.json not found. Please create it from the template in README.md
)

echo.
echo ✅ Setup completed successfully!
echo.
echo 📋 Next steps:
echo 1. Update local.settings.json with your Azure credentials
echo 2. Start the function: func start
echo 3. Test health endpoint: curl http://localhost:7071/api/health
echo.
echo 🔗 Local endpoints:
echo    Health Check: http://localhost:7071/api/health
echo    Claim Processing: http://localhost:7071/api/claim
echo    Cosmos Test: http://localhost:7071/api/test-cosmos
echo.
echo 🎉 Ready for development!
pause
