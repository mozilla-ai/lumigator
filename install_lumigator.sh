#!/bin/bash

# This script supports the initial setup of Lumigator for developing and using all functionalities locally.
# It requires Docker and Docker Compose to run. If they are not present on your machine, the script will install and activate them for you.
# If the local option is selected, Lumigator code is expected to be located in the current folder or in the provided folder.
# If a method is selected, it will install Lumigator using Git or a Zip file, depending on the case, and will place the files in selected_folder/lumigator.

# Help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Starts Lumigator by checking your setup or installing it."
    echo ""
    echo "Options:"
    echo "  -d, --directory DIR   Specify root directory (default: current directory)"
    echo "  -m, --method METHOD   Download method: 'git' or 'zip' (default: zip)"
    echo "  -o, --overwrite       Overwrite existing directory (lumigator)"
    echo "  -l, --local           Use local files in the same directory as the script (execute everything from the current directory without downloading anything)"
    echo "  -h, --help            Display this help message"
    exit 0
}

# Install Git on Linux
install_git_linux() {
    if ! command -v git &> /dev/null
    then
        echo "Git not found. Installing Git..."
        sudo apt-get update
        sudo apt-get install -y git
        echo "Git installed successfully."
    else
        echo "Git is already installed."
    fi
}

# Install Git on macOS
install_git_macos() {
    if ! command -v git &> /dev/null
    then
        echo "Git not found. Installing Git..."
        # Check if Homebrew is installed
        if ! command -v brew &> /dev/null
        then
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install git
        echo "Git installed successfully."
    else
        echo "Git is already installed."
    fi
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

# Install Docker on macOS
install_docker_macos() {
    if ! command -v docker &> /dev/null
    then
        echo "Docker not found. Installing Docker..."
        # Check if Homebrew is installed
        if ! command -v brew &> /dev/null
        then
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install --cask docker
        open -a Docker
        echo "Docker installed. Please complete the installation in the Docker Desktop app."
    else
        echo "Docker is already installed."
    fi
}

# Install Docker Compose
install_docker_compose() {
    if ! command -v docker-compose &> /dev/null
    then
        echo "Docker Compose not found. Installing Docker Compose..."
        case "$OSTYPE" in
            linux-gnu*)
                sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                sudo chmod +x /usr/local/bin/docker-compose
                ;;
            darwin*)
                brew install docker-compose
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

# Check Git is installed
check_git() {
    if ! command -v git &> /dev/null
    then
        echo "Git not found. Please install Git and try again."
        exit 1
    fi
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
download_method="git"
root_dir="$PWD"
overwrite=false
local_option=false
repo_name="lumigator"
repo_url="https://github.com/mozilla-ai/lumigator"
target_dir=""


# Command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -d|--directory)
            root_dir="$2"
            shift ;;
        -m|--method)
            if [[ "$2" != "git" && "$2" != "zip" ]]; then
                echo "Invalid method. Use 'git' or 'zip'."
                exit 1
            fi
            download_method="$2";
            shift ;;
        -o|--overwrite) overwrite=true ;;
        -l|--local) local_option=true ;;
        -h|--help) show_help ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done


# Download and install function
install_project() {

    target_dir="$root_dir/$repo_name"
    # Check if directory exists and handle overwrite
    if [ -d "$target_dir" ]; then
        if [ "$overwrite" = true ]; then
            echo "Overwriting existing directory..."
            echo "Deleting $target_dir"
            rm -rf "$target_dir"
            mkdir -p "$target_dir"

        else
            echo "Directory $target_dir already exists. Use -o to overwrite."
            exit 1
        fi
    else
        # Installation directory created, didn't exist
        mkdir -p "$target_dir"
    fi

    # Download based on method
    if [ "$download_method" == "git" ]; then
        echo "Cloning repository using Git..."
        cd "$target_dir" || exit 1
        git clone "${repo_url}.git" "$target_dir"
    elif [ "$download_method" == "zip" ]; then
        echo "Downloading ZIP file..."
        curl -L "${repo_url}/archive/main.zip" -o lumigator.zip
        unzip lumigator.zip > /dev/null
        echo "Moving extracted contents to $target_dir"
        mv lumigator-main/* "$target_dir"
        mv lumigator-main/.* "$target_dir" 2>/dev/null || true
        rmdir lumigator-main
        rm lumigator.zip
    fi
}

# Main execution
main() {
    echo "          *****************************************************************************************"
    echo "          *************************** STARTING LUMIGATOR BY MOZILLA.AI ****************************"
    echo "          *****************************************************************************************"

    # Detect OS and install base software
    detect_os

    case "$OS" in
        linux)
            install_docker_linux
            install_git_linux
            ;;
        macos)
            install_docker_macos
            install_git_macos
            ;;
    esac
    # Check if Docker is running
    check_docker_running

    # Install additional dependencies
    install_docker_compose

    # Verify Git is installed
    check_git

    if [ "$local_option" = false ]; then
        # Install the project
        install_project
    else
        target_dir="$root_dir"
        echo "Using local files..."
    fi


    cd $target_dir || error 1

    # Start the Lumigator service
    if [ -f "Makefile" ]; then
        make start-lumigator || {
            echo "Failed to start Lumigator. Check if your Docker service is active."
            exit 1        
        }
    else
        echo "Makefile to build and start $repo_name not found"
        exit 1
    fi

    # Open the browser
    case "$OSTYPE" in
        linux-gnu*) xdg-open http://localhost:80 ;;
        darwin*)    open http://localhost:80 ;;
        *)          echo "Browser launch not supported for this OS" ;;
    esac
}

# Run the main function
main
