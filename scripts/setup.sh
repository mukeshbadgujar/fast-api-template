#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check Python version
check_python_version() {
    local version=$1
    if command -v python$version &> /dev/null; then
        echo "Python $version found"
        return 0
    else
        echo "Python $version not found"
        return 1
    fi
}

# Function to create virtual environment
create_venv() {
    local version=$1
    echo -e "${YELLOW}Creating virtual environment with Python $version...${NC}"
    python$version -m venv venv
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Virtual environment created successfully${NC}"
        return 0
    else
        echo -e "${RED}Failed to create virtual environment${NC}"
        return 1
    fi
}

# Function to activate virtual environment
activate_venv() {
    if [ -d "venv" ]; then
        echo -e "${YELLOW}Activating virtual environment...${NC}"
        source venv/bin/activate
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Virtual environment activated${NC}"
            return 0
        else
            echo -e "${RED}Failed to activate virtual environment${NC}"
            return 1
        fi
    else
        echo -e "${RED}Virtual environment not found${NC}"
        return 1
    fi
}

# Function to install dependencies
install_dependencies() {
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements-dev.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Dependencies installed successfully${NC}"
        return 0
    else
        echo -e "${RED}Failed to install dependencies${NC}"
        return 1
    fi
}

# Function to create .env file
create_env_file() {
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > .env << EOL
# Application Settings
APP_NAME=fastapi-template
APP_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here
API_V1_STR=/api/v1

# Database Settings
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fastapi
DATABASE_URL=postgresql+asyncpg://\${POSTGRES_USER}:\${POSTGRES_PASSWORD}@\${POSTGRES_SERVER}/\${POSTGRES_DB}

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Monitoring Settings
ENABLE_METRICS=True
ENABLE_TRACING=True
TRACING_SERVICE_NAME=\${APP_NAME}

# External Services
EXTERNAL_SERVICE_TIMEOUT=30
EXTERNAL_SERVICE_RETRIES=3
EOL
    echo -e "${GREEN}.env file created successfully${NC}"
    echo -e "${YELLOW}Please update the .env file with your specific values${NC}"
}

# Main script
echo -e "${GREEN}FastAPI Template Setup Script${NC}"

# Check Python versions
echo -e "${YELLOW}Checking available Python versions...${NC}"
versions=("3.9" "3.10" "3.11" "3.12")
available_versions=()

for version in "${versions[@]}"; do
    if check_python_version $version; then
        available_versions+=($version)
    fi
done

if [ ${#available_versions[@]} -eq 0 ]; then
    echo -e "${RED}No suitable Python version found. Please install Python 3.9 or higher.${NC}"
    exit 1
fi

# Ask user to choose Python version
echo -e "${YELLOW}Available Python versions: ${available_versions[*]}${NC}"
read -p "Enter Python version to use (default: ${available_versions[0]}): " python_version

if [ -z "$python_version" ]; then
    python_version=${available_versions[0]}
fi

# Validate chosen version
if [[ ! " ${available_versions[*]} " =~ " ${python_version} " ]]; then
    echo -e "${RED}Invalid Python version selected${NC}"
    exit 1
fi

# Create virtual environment
create_venv $python_version || exit 1

# Activate virtual environment
activate_venv || exit 1

# Install dependencies
install_dependencies || exit 1

# Create .env file
create_env_file

echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update the .env file with your specific values"
echo "2. Run 'docker-compose up -d' to start the services"
echo "3. Run 'alembic upgrade head' to apply database migrations"
echo "4. Start the development server with 'uvicorn app.main:app --reload'" 