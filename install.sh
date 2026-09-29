#!/usr/bin/env bash

set -e

PROJECT_DIR="/root/metatrader"
REPOSITORY="https://github.com/sina1991/30nAtrader.git"
VENV_DIR="${PROJECT_DIR}/venv"
SERVICE_FILE="/etc/systemd/system/metatrader-dashboard.service"

echo "========================================"
echo "30nAtrader installer"
echo "========================================"

echo "[1/6] Installing system packages..."

apt-get update

apt-get install -y \
    git \
    python3 \
    python3-venv \
    python3-pip

echo "[1/6] System packages installed."

echo "[2/6] Cloning repository..."

if [ -d "${PROJECT_DIR}/.git" ]; then
    echo "Repository already exists: ${PROJECT_DIR}"
else
    git clone "${REPOSITORY}" "${PROJECT_DIR}"
fi

echo "[2/6] Repository ready."

echo "[3/6] Creating Python virtual environment..."

if [ -d "${VENV_DIR}" ]; then
    echo "Virtual environment already exists: ${VENV_DIR}"
else
    python3 -m venv "${VENV_DIR}"
fi

echo "[3/6] Virtual environment ready."

echo "[4/6] Installing Python packages..."

"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/pip" install -r "${PROJECT_DIR}/requirements.txt"

echo "[4/6] Python packages installed."

echo "[5/6] Configuring systemd service..."

cat <<SERVICE_EOF > "${SERVICE_FILE}"
[Unit]
Description=30nAtrader XAUUSD Dashboard
After=network.target

[Service]
Type=simple
WorkingDirectory=${PROJECT_DIR}
ExecStart=${VENV_DIR}/bin/python ${VENV_DIR}/bin/uvicorn web.app:app --host 0.0.0.0 --port 8090
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE_EOF

systemctl daemon-reload
systemctl enable metatrader-dashboard.service

echo "[5/6] systemd service configured."

echo "[6/6] Starting dashboard..."

systemctl restart metatrader-dashboard.service

echo "[6/6] Dashboard started."

echo "========================================"
echo "30nAtrader installation completed."
echo "Dashboard: http://SERVER_IP:8090"
echo "========================================"
