#!/bin/bash

# This script supports the initial setup of Lumigator for developing and using all functionalities locally.
# It requires Docker and Docker Compose to run. If they are not present on your machine, the script will install and activate them for you.
# If the local option (`-l`) is selected, Lumigator code is expected to be located in the current folder or in the provided folder.

# Help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Starts Lumigator by checking your setup or installing it."
    echo ""
    echo "Options:"
    echo "  -d, --directory DIR   Specify the directory for installing the code (default: inside current directory)"
    echo "  -o, --overwrite       Overwrite existing directory (lumigator)"
    echo "  -h, --help            Display this help message"
    exit 0
}



# Install Docker on Linux
install_docker_linux() {
    if ! command -v docker &> /dev/null
    then
        echo "Docker not found. Installing Docker..."
        sudo apt-get update
        sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io
        sudo usermod -aG docker $USER
        echo "Docker installed successfully."
    else
        echo "Docker is already installed."
    fi
}


# Install Brew in OSX
install_brew_macos() {
    if [ -x "$BREW_PATH" ]; 
    then
        echo "Brew is already installed"
    else
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        eval "$($BREW_PATH/brew shellenv)"     
    fi
}


# Install Docker on macOS
install_docker_macos() {
    if ! command -v docker &> /dev/null
    then
        echo "Docker not found. Installing Docker..."
        echo "!!! Docker has some issues running on Mac OS with the latest version and it needs some workaournd to fix the issue. Please check docker website and install manually"
        exit

        # Check if Homebrew is installed
        $BREW_PATH/brew install --cask docker
        open -a Docker
        echo "Docker installed. Please complete the installation in the Docker Desktop app."
    else
        echo "Docker is already installed."
    fi
}


# Install Docker Compose
install_docker_compose() {
    if ! command -v "$BREW_PATH/docker-compose" &> /dev/null
    then
        echo "Docker Compose not found. Installing Docker Compose..."
        case "$OSTYPE" in
            linux-gnu*)
                sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                sudo chmod +x /usr/local/bin/docker-compose
                ;;
            darwin*)
                "$BREW_PATH/brew" install docker-compose
                ;;
            *)
                echo "Unsupported OS for Docker Compose installation"
                exit 1
                ;;
        esac
        echo "Docker Compose installed successfully."
    else
        echo "Docker Compose is already installed."
    fi
}

# Detect the OS
detect_os() {
    OS="Undefined"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        echo "Unsupported OS: $OSTYPE"
        exit 1
    fi
    echo "Operating System detected: $OS"
}



# Check if Docker is running
check_docker_running() {
    if ! docker info &> /dev/null
    then
        echo "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}


# Default values
ROOT_DIR="$PWD"
OVERWRITE=false
REPO_NAME="lumigator"
FOLDER_NAME="lumigator_code"
REPO_URL="https://github.com/mozilla-ai/lumigator"
TARGET_DIR=""
BREW_PATH="/opt/homebrew/bin/"
LUMIGATOR_URL="http://localhost:80"


# Command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -d|--directory)
            ROOT_DIR="$2"
            shift ;;
        -m|--method)
            if [[ "$2" != "git" && "$2" != "zip" ]]; then
                echo "Invalid method. Use 'git' or 'zip'."
                exit 1
            fi
            download_method="$2";
            shift ;;
        -o|--overwrite) OVERWRITE=true ;;
        -l|--local) local_option=true ;;
        -h|--help) show_help ;;
        *) echo "!!!! Unknown parameter passed: $1 Please check the help command"; 
        show_help
        exit 1 ;;
    esac
    shift
done


# Download and install function
install_project() {

    TARGET_DIR="$ROOT_DIR/$FOLDER_NAME"
    # Check if directory exists and handle overwrite
    if [ -d "$TARGET_DIR" ]; then
        if [ "$OVERWRITE" = true ]; then
            echo "Overwriting existing directory..."
            echo "Deleting $TARGET_DIR"
            rm -rf "$TARGET_DIR"
            mkdir -p "$TARGET_DIR"

        else
            echo "Directory $TARGET_DIR already exists. Use -o to overwrite."
            exit 1
        fi
    else
        # Installation directory created, didn't exist
        mkdir -p "$TARGET_DIR"
    fi

    # Download based on method
 
        echo "Downloading ZIP file..."
        curl -L "${REPO_URL}/archive/main.zip" -o lumigator.zip
        unzip lumigator.zip > /dev/null
        echo "Moving extracted contents to $TARGET_DIR"
        mv lumigator-main/* "$TARGET_DIR"
        mv lumigator-main/.* "$TARGET_DIR" 2>/dev/null || true
        rmdir lumigator-main
        rm lumigator.zip
}

# Main execution
main() {
    echo "*****************************************************************************************"
    echo "*************************** STARTING LUMIGATOR BY MOZILLA.AI ****************************"
    echo "*****************************************************************************************"

    # Detect OS and install base software
    detect_os

    case "$OS" in
        linux)
            install_docker_linux
            ;;
        macos)
            install_brew_macos
            install_docker_macos
            ;;
    esac
    # Check if Docker is running
    check_docker_running

    # Install additional dependencies
    install_docker_compose


        install_project



    cd $TARGET_DIR || error 1



    # Start the Lumigator service
    if [ -f "Makefile" ]; then
        make start-lumigator || {
            echo "Failed to start Lumigator. Check if your Docker service is active."
            exit 1        
        }
    else
        echo "Makefile to build and start $REPO_NAME not found"
        exit 1
    fi

    # Open the browser
    case "$OSTYPE" in
        linux-gnu*) xdg-open $LUMIGATOR_URL ;;
        darwin*)    open $LUMIGATOR_URL ;;
        *)          echo "Browser launch not supported for this OS. Type $LUMIGATOR_URL in your browser" ;;
    esac
    echo "To close $REPO_NAME, close $LUMIGATOR_URL in your browsers and type make stop-lumigator in your console inside the $TARGET_DIR folder"
}

# Run the main function
main
