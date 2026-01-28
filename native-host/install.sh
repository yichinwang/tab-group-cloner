#!/bin/bash
# Installation script for Tab Group Cloner Native Messaging Host (macOS/Linux)

set -e

echo "======================================"
echo "Tab Group Cloner - Native Host Setup"
echo "======================================"
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    MANIFEST_DIR="$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    MANIFEST_DIR="$HOME/.config/google-chrome/NativeMessagingHosts"
else
    echo "Unsupported operating system: $OSTYPE"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="$SCRIPT_DIR/tab_cloner_host.py"

echo "Detected OS: $OS"
echo "Script location: $SCRIPT_DIR"
echo ""

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "Found: $PYTHON_VERSION"
echo ""

# Create virtual environment and install dependencies
VENV_DIR="$SCRIPT_DIR/venv"
echo "Creating virtual environment at $VENV_DIR..."
python3 -m venv "$VENV_DIR"

echo "Installing Python dependencies..."
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
echo ""

# Create a wrapper script that uses the venv
echo "Creating wrapper script..."
WRAPPER_SCRIPT="$SCRIPT_DIR/tab_cloner_host_wrapper.sh"
cat > "$WRAPPER_SCRIPT" <<WRAPPER
#!/bin/bash
"$VENV_DIR/bin/python3" "$PYTHON_SCRIPT" "\$@"
WRAPPER
chmod +x "$WRAPPER_SCRIPT"

# Make the Python script executable
echo "Making Python script executable..."
chmod +x "$PYTHON_SCRIPT"
echo ""

# Create manifest directory
echo "Creating manifest directory..."
mkdir -p "$MANIFEST_DIR"
echo ""

# Create the manifest file
echo "Creating native messaging host manifest..."
MANIFEST_FILE="$MANIFEST_DIR/com.tabcloner.host.json"

cat > "$MANIFEST_FILE" <<EOF
{
  "name": "com.tabcloner.host",
  "description": "Tab Group Cloner Native Messaging Host",
  "path": "$WRAPPER_SCRIPT",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://EXTENSION_ID_PLACEHOLDER/"
  ]
}
EOF

echo "Manifest created at: $MANIFEST_FILE"
echo ""

# Inform user about next steps
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Install the Chrome extension"
echo "2. Note the extension ID from chrome://extensions"
echo "3. Edit the manifest file and replace EXTENSION_ID_PLACEHOLDER with your actual extension ID:"
echo "   $MANIFEST_FILE"
echo ""
echo "4. Install Sidekick browser from https://www.meetsidekick.com/"
echo "5. Install ChromeDriver: brew install chromedriver (macOS) or download from https://chromedriver.chromium.org/"
echo ""
echo "Logs will be written to: $HOME/tab_cloner_host.log"
echo ""
