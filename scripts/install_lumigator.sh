#!/bin/bash
#
# install_lumigator.sh
#
# A script to set up Lumigator locally, installing Docker and Docker Compose as needed.
# Working for macOS and Linux (root-based and rootless Docker scenarios).

set -e

# Help
show_help() {
  echo "Usage: $0 [OPTIONS]"
  echo "Sets up Lumigator by checking your environment and installing dependencies."
  echo ""
  echo "Options:"
  echo "  -d, --directory DIR   Specify the directory for installing the code (default: current directory)"
  echo "  -o, --overwrite       Overwrite existing directory (lumigator_code)"
  echo "  -m, --main            Use GitHub main branch of Lumigator (default is MVP tag)"
  echo "  -h, --help            Display this help message"
  exit 0
}

######################################
# Helper Functions
######################################

log() {
  printf '%s\n' "$*"
}

check_docker_installed() {
  type docker >/dev/null 2>&1 && return 0
  return 1
}

check_docker_running() {
  docker info >/dev/null 2>&1 && return 0
  log "Docker daemon is NOT running."
  return 1
}

check_compose_installed() {
  docker compose version >/dev/null 2>&1 && return 0  
  return 1
}

detect_os_and_arch() {
  OS_TYPE=$(uname -s | tr '[:upper:]' '[:lower:]')
  case "$OS_TYPE" in
  linux*) OS_TYPE="linux" ;;
  darwin*) OS_TYPE="macos" ;;
  *)
    log "Unsupported OS: $OS_TYPE"
    exit 1
    ;;
  esac

  ARCH=$(uname -m)
  case "$ARCH" in
  x86_64) COMPOSE_ARCH="x86_64" ;;
  aarch64) COMPOSE_ARCH="aarch64" ;;
  armv7l) COMPOSE_ARCH="armv7" ;;
  arm64) COMPOSE_ARCH="arm64" ;;
  *)
    log "Unsupported architecture: $ARCH"
    log "Supported: x86_64, aarch64, armv7l, arm64"
    exit 1
    ;;
  esac
  log "Detected OS: $OS_TYPE, Architecture: $ARCH"
}

get_latest_compose_version() {
  log "Fetching latest Docker Compose version..." >&2
  if ! command -v curl >/dev/null 2>&1; then
    log "Error: curl is required to fetch the latest version." >&2
    exit 1
  fi
  latest_version=$(curl -s "https://api.github.com/repos/docker/compose/releases/latest" | grep '"tag_name":' | sed 's/.*"tag_name": "\(.*\)",/\1/' 2>/dev/null)
  if [ -z "$latest_version" ]; then
    log "Error: Failed to fetch latest Docker Compose version." >&2
    exit 1
  fi
  log "Latest version detected: $latest_version" >&2
  printf '%s' "$latest_version"
}

######################################
# Installation Functions
######################################

install_docker_macos() {
  log "==> Installing Docker and Compose on macOS via Docker Desktop..."
  if check_docker_installed && check_compose_installed && check_docker_running; then
    log "Docker and Compose are already set up."
    return 0
  fi

  if command -v brew >/dev/null 2>&1; then
    log "Installing Docker Desktop via Homebrew (includes Compose v2)..."
    brew install --cask docker
  else
    log "Homebrew not found. Installing Docker Desktop manually via DMG..."
    if [ "$ARCH" = "arm64" ]; then
      DMG_URL="https://desktop.docker.com/mac/main/arm64/Docker.dmg"
    else
      DMG_URL="https://desktop.docker.com/mac/main/amd64/Docker.dmg"
    fi
    log "Downloading Docker Desktop DMG from: $DMG_URL"
    curl -L -o /tmp/Docker.dmg "$DMG_URL"
    log "Mounting DMG..."
    hdiutil attach /tmp/Docker.dmg -mountpoint /Volumes/Docker -nobrowse
    log "Copying Docker.app to /Applications (requires admin privileges)..."
    sudo cp -R "/Volumes/Docker/Docker.app" /Applications/
    log "Unmounting DMG..."
    hdiutil detach /Volumes/Docker
    log "Cleaning up DMG..."
    rm -f /tmp/Docker.dmg
  fi

  log "Starting Docker Desktop..."
  open -a Docker
  log "Waiting for Docker to start..."
  until docker info >/dev/null 2>&1; do
    sleep 2
    log "Still waiting for Docker..."
  done
  log "Docker Desktop (with Compose) is running!"
}

detect_distro() {
  . /etc/os-release
  if [ "$ID" = "debian" ]; then
    echo "debian"
  elif [ "$ID" = "ubuntu" ]; then
    echo "ubuntu"
  else
    echo "unsupported"
  fi
}

install_docker_linux_root() {
  DISTRO=$(detect_distro)
  if [ "$DISTRO" = "unsupported" ]; then
    log "Error: Unsupported Linux distribution."
    exit 1
  fi

  log "==> Installing Docker and Compose (root-based) on $DISTRO..."
  sudo mkdir -p /etc/apt/keyrings
  GPG_KEY="/etc/apt/keyrings/docker.gpg"
  if [ -f "$GPG_KEY" ]; then
    log "Docker GPG key already exists. Removing and re-downloading..."
    sudo rm -f "$GPG_KEY"
  fi
  curl -fsSL "https://download.docker.com/linux/$DISTRO/gpg" | sudo gpg --dearmor -o "$GPG_KEY"
  sudo chmod a+r "$GPG_KEY"
  echo "deb [arch=$(dpkg --print-architecture) signed-by=$GPG_KEY] https://download.docker.com/linux/$DISTRO $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update -y
  sudo apt-get install -y ca-certificates curl gnupg lsb-release
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  sudo systemctl enable docker
  sudo systemctl start docker
  sudo usermod -aG docker "$USER"
  log "Docker and Compose installed. Log out and back in for group changes to take effect."
}

detect_docker_mode() {
  if systemctl is-active --quiet docker; then
    echo "root"
  elif systemctl --user is-active --quiet docker; then
    echo "rootless"
  else
    echo "unknown"
  fi
}

configure_docker_host() {
  DOCKER_MODE=$(detect_docker_mode)
  if [ "$DOCKER_MODE" = "rootless" ]; then
    log "Configuring DOCKER_HOST for rootless mode..."
    export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock
    if ! grep -q "DOCKER_HOST=unix://" ~/.bashrc; then
      echo "export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock" >> ~/.bashrc
    fi
    if ! grep -q "DOCKER_HOST=unix://" ~/.profile; then
      echo "export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock" >> ~/.profile
    fi
    log "DOCKER_HOST set to: $DOCKER_HOST"
  elif [ "$DOCKER_MODE" = "root" ]; then
    log "Using system-wide Docker (root installation). No DOCKER_HOST override needed."
    unset DOCKER_HOST
    sed -i '/DOCKER_HOST=/d' ~/.bashrc
    sed -i '/DOCKER_HOST=/d' ~/.profile
  else
    log "Warning: Could not determine Docker installation mode."
  fi
}

install_docker_linux_rootless() {
  USER_HOME="$HOME"
  BIN_DIR="$USER_HOME/bin"
  CLI_PLUGINS_DIR="$USER_HOME/.docker/cli-plugins"
  XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-/run/user/$(id -u)}
  DOCKER_SOCK="$XDG_RUNTIME_DIR/docker.sock"
  DOCKER_VERSION="20.10.24"
  SLIRP4NETNS_VERSION="1.2.0"
  DOCKER_ROOTLESS_DIR="$USER_HOME/.docker-rootless"
  COMPOSE_VERSION=$(get_latest_compose_version)
  COMPOSE_URL="https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-${COMPOSE_ARCH}"

  log "==> Installing Docker $DOCKER_VERSION and Compose $COMPOSE_VERSION (rootless)..."

  # Added prerequisite check statement be sure you have all those before installing docker in rootless mode
  log "Prerequisites: Ensure 'uidmap' package is installed (e.g., 'sudo apt install uidmap') for newuidmap/newgidmap."
  log "Also ensure user namespaces are enabled and sub-UID/GID ranges are set in /etc/subuid and /etc/subgid."
  log "Check with your IT administrator if you are unsure."

  if [ "$(id -u)" -eq 0 ]; then
    log "Error: This should not run as root for rootless mode."
    exit 1
  fi

  log "Checking prerequisites..."
  for cmd in curl tar newuidmap newgidmap; do
    if ! type "$cmd" >/dev/null 2>&1; then
      log "Error: $cmd is required. Install with 'sudo apt install uidmap' (needs admin)."
      exit 1
    fi
  done

  if ! unshare --user --pid echo YES >/dev/null 2>&1; then
    log "Error: User namespaces not supported or enabled."
    exit 1
  fi

  USER_NAME=$(whoami)
  if ! grep -q "^$USER_NAME:" /etc/subuid || ! grep -q "^$USER_NAME:" /etc/subgid; then
    log "Error: Sub-UID/GID ranges missing for $USER_NAME."
    log "Run: 'sudo usermod -v 100000-165535 -w 100000-165535 $USER_NAME' to fix."
    exit 1
  fi

  if [ ! -w "$XDG_RUNTIME_DIR" ]; then
    log "Warning: $XDG_RUNTIME_DIR not writable. Using $USER_HOME/run instead."
    XDG_RUNTIME_DIR="$USER_HOME/run"
    DOCKER_SOCK="$XDG_RUNTIME_DIR/docker.sock"
    mkdir -p "$XDG_RUNTIME_DIR" || { log "Error: Cannot create $XDG_RUNTIME_DIR"; exit 1; }
  fi

  log "Cleaning up existing Docker files..."
  systemctl --user stop docker.service 2>/dev/null || true
  rm -rf "$DOCKER_ROOTLESS_DIR" "$BIN_DIR/docker"* "$USER_HOME/.local/share/docker" "$USER_HOME/.config/systemd/user/docker.service" "$BIN_DIR/slirp4netns" "$CLI_PLUGINS_DIR/docker-compose"

  mkdir -p "$DOCKER_ROOTLESS_DIR" "$BIN_DIR" "$USER_HOME/.local/share/docker" "$CLI_PLUGINS_DIR"

  log "Downloading Docker $DOCKER_VERSION..."
  curl -fsSL "https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKER_VERSION}.tgz" -o "$DOCKER_ROOTLESS_DIR/docker.tgz" || { log "Error: Failed to download Docker"; exit 1; }
  tar -xzf "$DOCKER_ROOTLESS_DIR/docker.tgz" -C "$BIN_DIR" --strip-components=1 || { log "Error: Failed to extract Docker"; exit 1; }

  log "Downloading rootless extras for Docker $DOCKER_VERSION..."
  curl -fsSL "https://download.docker.com/linux/static/stable/x86_64/docker-rootless-extras-${DOCKER_VERSION}.tgz" -o "$DOCKER_ROOTLESS_DIR/docker-rootless.tgz" || { log "Error: Failed to download rootless extras"; exit 1; }
  tar -xzf "$DOCKER_ROOTLESS_DIR/docker-rootless.tgz" -C "$BIN_DIR" --strip-components=1 || { log "Error: Failed to extract rootless extras"; exit 1; }

  log "Downloading slirp4netns $SLIRP4NETNS_VERSION..."
  curl -fsSL "https://github.com/rootless-containers/slirp4netns/releases/download/v${SLIRP4NETNS_VERSION}/slirp4netns-x86_64" -o "$BIN_DIR/slirp4netns" || { log "Error: Failed to download slirp4netns"; exit 1; }
  chmod +x "$BIN_DIR/slirp4netns"

  log "Downloading Docker Compose $COMPOSE_VERSION..."
  curl -fsSL "$COMPOSE_URL" -o "$CLI_PLUGINS_DIR/docker-compose" || { log "Error: Failed to download Compose"; exit 1; }
  chmod +x "$CLI_PLUGINS_DIR/docker-compose"

  for bin in docker dockerd containerd runc containerd-shim-runc-v2 dockerd-rootless.sh rootlesskit; do
    if [ -f "$BIN_DIR/$bin" ]; then
      chmod +x "$BIN_DIR/$bin"
    else
      log "Error: Required binary $bin not found in $BIN_DIR"
      exit 1
    fi
  done

  log "Setting environment variables..."
  echo "export PATH=$BIN_DIR:\$PATH" > "$USER_HOME/.bashrc.docker"
  echo "export DOCKER_HOST=unix://$DOCKER_SOCK" >> "$USER_HOME/.bashrc.docker"
  grep -q ".bashrc.docker" "$USER_HOME/.bashrc" || echo ". $USER_HOME/.bashrc.docker" >> "$USER_HOME/.bashrc"
  . "$USER_HOME/.bashrc.docker"

  log "Setting up systemd user service..."
  mkdir -p "$USER_HOME/.config/systemd/user"

  cat << EOF > "$USER_HOME/.config/systemd/user/docker.service"
[Unit]
Description=Docker Rootless Daemon
After=network.target

[Service]
ExecStart=$BIN_DIR/dockerd-rootless.sh --data-root $USER_HOME/.local/share/docker --pidfile $DOCKER_ROOTLESS_DIR/docker.pid --log-level debug --userland-proxy=true --userland-proxy-path=$BIN_DIR/slirp4netns --bridge=none --iptables=false --exec-opt native.cgroupdriver=cgroupfs
Environment="PATH=$BIN_DIR:/usr/local/bin:/usr/bin:/bin"
Environment="DOCKER_HOST=unix://$DOCKER_SOCK"
Restart=always
Type=simple

[Install]
WantedBy=default.target
EOF

  systemctl --user daemon-reload
  systemctl --user enable docker.service
  systemctl --user start docker.service

  # Docker startup 
  log "Waiting for Docker to start..."
  for i in {1..10}; do
    if docker info >/dev/null 2>&1; then
      log "Docker is running."
      break
    fi
    sleep 3
  done
  if ! docker info >/dev/null 2>&1; then
    log "Error: Docker daemon failed to start after 30 seconds."
    systemctl --user status docker.service
    journalctl --user -u docker.service --no-pager | tail -n 20
    exit 1
  fi

  log "Verifying Docker with hello-world container..."
  if "$BIN_DIR/docker" run --rm hello-world; then
    log "Docker test passed."
  else
    log "Error: Docker test failed."
    systemctl --user status docker.service
    journalctl --user -u docker.service --no-pager | tail -n 20
    exit 1
  fi

  log "Verifying Docker Compose..."
  if "$BIN_DIR/docker" compose version; then
    log "Docker Compose is installed."
  else
    log "Error: Docker Compose verification failed."
    exit 1
  fi

  log "Docker $DOCKER_VERSION and Compose $COMPOSE_VERSION rootless installed successfully!"
}

install_docker_and_compose() {
  log "This script will install the latest Docker and Docker Compose, then set up Lumigator."
  read -p "Proceed? (yes/no): " user_response
  if [ "$user_response" != "yes" ]; then
    log "Aborting installation."
    exit 0
  fi

  detect_os_and_arch

  case "$OS_TYPE" in
  macos)
    install_docker_macos
    ;;
  linux)
    if check_docker_installed && check_compose_installed && check_docker_running; then
      log "Docker and Compose are already set up."
    else
      log "Do you want to install Docker and Compose in rootless mode (y) or root-based mode (n)? (y/N): "
      read -r resp
      case "$resp" in
      [yY]*)
        install_docker_linux_rootless
        DOCKER_INSTALL_MODE="rootless"
        ;;
      *)
        install_docker_linux_root
        DOCKER_INSTALL_MODE="root"
        ;;
      esac
    fi
    configure_docker_host
  ;;
  *)
    log "Unsupported OS: $OS_TYPE"
    exit 1
    ;;
  esac
  log "Docker and Compose installation complete."
}

install_project() {
  LUMIGATOR_TARGET_DIR="$LUMIGATOR_ROOT_DIR/$LUMIGATOR_FOLDER_NAME"
  log "Installing Lumigator in $LUMIGATOR_TARGET_DIR"

  if [ -d "$LUMIGATOR_TARGET_DIR" ]; then
    if [ "$OVERWRITE_LUMIGATOR" = true ]; then
      log "Overwriting existing directory..."
      rm -rf "$LUMIGATOR_TARGET_DIR"
    else
      log "Directory $LUMIGATOR_TARGET_DIR exists. Use -o to overwrite."
      exit 1
    fi
  fi
  mkdir -p "$LUMIGATOR_TARGET_DIR"

  log "Downloading Lumigator ${LUMIGATOR_REPO_TAG}${LUMIGATOR_VERSION}..."
  curl -L -o "lumigator.zip" "${LUMIGATOR_REPO_URL}/archive/${LUMIGATOR_REPO_TAG}${LUMIGATOR_VERSION}.zip" || { log "Error: Failed to download Lumigator"; exit 1; }
  unzip lumigator.zip >/dev/null || { log "Error: Failed to unzip Lumigator"; exit 1; }
  mv lumigator-${LUMIGATOR_VERSION}/* "$LUMIGATOR_TARGET_DIR" || { log "Error: Failed to move Lumigator files"; exit 1; }
  mv lumigator-${LUMIGATOR_VERSION}/.* "$LUMIGATOR_TARGET_DIR" 2>/dev/null || true
  rmdir lumigator-${LUMIGATOR_VERSION}
  rm lumigator.zip

  if [ "$DOCKER_INSTALL_MODE" = "rootless" ]; then
    log "Patching docker-compose.yaml for rootless mode: changing frontend port from 80 to 8080."
    sed -i 's/- 80:80/- 8080:80/g' "$LUMIGATOR_TARGET_DIR/docker-compose.yaml"
    LUMIGATOR_URL="http://localhost:8080"
  else
    LUMIGATOR_URL="http://localhost:80"
  fi
}

main() {
  echo "*****************************************************************************************"
  echo "*************************** STARTING LUMIGATOR BY MOZILLA.AI ****************************"
  echo "*****************************************************************************************"

  LUMIGATOR_ROOT_DIR="$PWD"
  OVERWRITE_LUMIGATOR=false
  LUMIGATOR_FOLDER_NAME="lumigator_code"
  LUMIGATOR_REPO_URL="https://github.com/mozilla-ai/lumigator"
  LUMIGATOR_REPO_TAG="refs/tags/v"
  LUMIGATOR_VERSION="0.1.0-alpha"
  LUMIGATOR_URL="http://localhost:80"  

  while [ "$#" -gt 0 ]; do
    case $1 in
    -d | --directory) LUMIGATOR_ROOT_DIR="$2"; shift ;;
    -o | --overwrite) OVERWRITE_LUMIGATOR=true ;;
    -m | --main) LUMIGATOR_REPO_TAG="refs/heads/"; LUMIGATOR_VERSION="main" ;;
    -h | --help) show_help ;;
    *) log "Unknown parameter: $1"; show_help ;;
    esac
    shift
  done

  log "Starting Lumigator setup..."
  for tool in curl unzip make; do
    type "$tool" >/dev/null 2>&1 || { log "Error: $tool required."; exit 1; }
  done

  install_docker_and_compose
  install_project

  cd "$LUMIGATOR_TARGET_DIR" || { log "Error: Cannot access $LUMIGATOR_TARGET_DIR"; exit 1; }
  if [ -f "Makefile" ]; then
    DOCKER_MODE=$(detect_docker_mode)
    if [ "$DOCKER_MODE" = "rootless" ]; then
      export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock
    fi
    log "Starting Lumigator..."
    make start-lumigator || { log "Failed to start Lumigator."; exit 1; }
  else
    log "Makefile not found in $LUMIGATOR_TARGET_DIR"
    exit 1
  fi

  log "Lumigator setup complete. Access at $LUMIGATOR_URL"
  case "$OS_TYPE" in
  linux) xdg-open "$LUMIGATOR_URL" 2>/dev/null || log "Open $LUMIGATOR_URL in your browser." ;;
  macos) open "$LUMIGATOR_URL" 2>/dev/null || log "Open $LUMIGATOR_URL in your browser." ;;
  *) log "Open $LUMIGATOR_URL in your browser." ;;
  esac
  log "To stop, run 'make stop-lumigator' in $LUMIGATOR_TARGET_DIR"
}

main "$@"