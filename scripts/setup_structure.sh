# Project structure
PROJECT_ROOT=.

# Main directories
SRC_DIR=${PROJECT_ROOT}/src
TESTS_DIR=${PROJECT_ROOT}/tests
DOCS_DIR=${PROJECT_ROOT}/docs
CONFIG_DIR=${PROJECT_ROOT}/config
SCRIPTS_DIR=${PROJECT_ROOT}/scripts
DATA_DIR=${PROJECT_ROOT}/data

# Create directories if they don't exist
mkdir -p ${SRC_DIR}/{core,research,rag,analysis,security,evaluation,dashboard}
mkdir -p ${TESTS_DIR}/{unit,integration,security,evaluation,dashboard}
mkdir -p ${DOCS_DIR}/{guides,api,architecture}
mkdir -p ${CONFIG_DIR}
mkdir -p ${SCRIPTS_DIR}
mkdir -p ${DATA_DIR}/{benchmarks,results,cache}

echo "Professional folder structure created successfully!"
