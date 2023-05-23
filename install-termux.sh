cd ~
if ! command -v lsof &> /dev/null; then
  echo "lsof is not installed. Installing lsof ..."
  pkg install -y lsof
fi

if ! command -v python3 &> /dev/null; then
  echo "Python 3 is not installed. Installing Python 3..."
  pkg install -y python
fi
if ! command -v python3 &> /dev/null; then
  echo "Python 3 is not installed. Installing Python 3..."
  pkg install -y python
fi
if dpkg -s openssl >/dev/null 2>&1; then
    echo "OpenSSL is installed."
else
    echo "OpenSSL is not installed. Installing OpenSSL..."
    pkg install -y openssl 
fi
if ! command -v sshd &> /dev/null; then
  echo "OpenSSH is not installed. Installing OpenSSH..."
  pkg install -y openssh
fi
if ! command -v unzip &> /dev/null; then
  echo "Unzip is not installed. Installing Unzip..."
  pkg install -y unzip 
fi
if ! command -v wget &> /dev/null; then
  echo "wget is not installed. Installing wget..."
  pkg install -y wget 
fi
package="libjpeg-turbo"
if pkg list-installed | grep -q "^$package"; then
    echo "$package is installed"
else
    echo "$package is not installed"
    pkg install -y libjpeg-turbo
fi



ssh-keygen -A
echo "Please enter a password for ssh connection:"
passwd
echo "Enabling termux-wake-lock && sshd"
termux-wake-lock && sshd

echo "Downloading the package..."
wget -qO qutline-printer.zip https://github.com/F4RAN/qutline-printer/archive/refs/heads/main.zip

DIRECTORY="qutline-printer-main"
if [ -d "$DIRECTORY" ]; then
    echo "Directory '$DIRECTORY' exists. Removing..."
    rm -r "$DIRECTORY"
    echo "Directory '$DIRECTORY' removed."
else
    echo "Directory '$DIRECTORY' does not exist."
fi

# Kill process on port 8080
ps aux | grep app.py | awk '{print $2}' | xargs kill -9

# Unzip the file
echo "Unzipping the file..."
unzip -q qutline-printer.zip
rm qutline-printer.zip

echo "Install and executing printer package"
cd "$DIRECTORY"
pip install virtualenv
virtualenv .venv
source .venv/bin/activate

# Manual Pillow Setup
pip install wheel
architecture=$(uname -m)
if [[ $architecture == "aarch64" ]]; then
    LDFLAGS="-L/system/lib64/" CFLAGS="-I/data/data/com.termux/files/usr/include/" pip install Pillow
elif [[ $architecture == "armv7l" ]]; then
    LDFLAGS="-L/system/lib/" CFLAGS="-I/data/data/com.termux/files/usr/include/" pip install Pillow
else
    echo "Unsupported architecture: $architecture"
    exit 1
fi
pip install -r requirements.txt
python app.py &


echo "Configure Boot Settings"
cd ~
BOOT_DIRECTORY="$HOME/.termux/boot"
SCRIPT_FILE="$BOOT_DIRECTORY/start-apps"
# Create the directory if it doesn't exist
mkdir -p "$BOOT_DIRECTORY"
# Check if the script file already exists and clear its content if not empty
if [ -f "$SCRIPT_FILE" ]; then
    if [ -s "$SCRIPT_FILE" ]; then
        > "$SCRIPT_FILE" # Clears the content of the file
    fi
fi

# Create the script file
cat > "$SCRIPT_FILE" << EOF
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock && sshd
cd $(readlink -f "./$DIRECTORY") && source .venv/bin/activate && python3 app.py run &

# Make the script executable
chmod u+x "$SCRIPT_FILE"

echo "Automation printer setup completed."
echo "After sleep or restarting device you dont loose anything."
echo "By F4RAN - Vitalize.dev 2023"


