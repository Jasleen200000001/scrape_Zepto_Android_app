# Create a virtual environment and install dependencies (PowerShell)
python -m venv .venv
Write-Output "Activating virtual environment..."
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Write-Output "Environment ready. To activate later run: . \.venv\Scripts\Activate.ps1"
