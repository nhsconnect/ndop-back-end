#!/bin/bash -e
set -e
set -o pipefail

BUILD_ID_PREFIX="/opt/thunderbird/builds/codebuild"
BUILD_ID_FILE="build-id.txt"

function startBuild () {
  local PROJECT_NAME=${1}
  local GIT_MARKER=${2}
  local FINAL_ID="none"
  local ID_FILE="${BUILD_ID_PREFIX}-${GIT_MARKER}-${PROJECT_NAME}-${BUILD_ID_FILE}"
  umask 0000 && echo "" > "${ID_FILE}"
  echo "aws codebuild start-build --project-name ${PROJECT_NAME} --source-version ${GIT_MARKER}"
  aws codebuild start-build --project-name ${PROJECT_NAME} --source-version ${GIT_MARKER} | jq --raw-output '.build | { id: .id, currentPhase: .currentPhase, buildStatus: .buildStatus, startTime: .startTime, sourceVersion: .sourceVersion } ' | tee ${ID_FILE}
  echo ""
  getBuildIdFromFile FINAL_ID ${ID_FILE}
  echo "BUILD_ID ${FINAL_ID} saved to ${ID_FILE}"
  echo ""
}

function getBuildIdFromFile () {
  #arg1 is a by-ref variable to fill in. Gotta love bash!
  local ID_FILE=${2}
  local BUILD_ID="not_set"
  echo "Loading file ${ID_FILE}:"
  local BUILD_ID_JSON=$(<${ID_FILE})
  BUILD_ID=$(echo ${BUILD_ID_JSON} | jq --raw-output '.id')
  echo "BUILD_ID from file = ${BUILD_ID}"
  eval "$1=\"${BUILD_ID}\""
}

function checkBuild () {
  local PROJECT_NAME=${1}
  local GIT_MARKER=${2}
  local USE_FILE=${3}
  local BUILD_ID=${4}
  local FINAL_ID="none"
  local ID_FILE="${BUILD_ID_PREFIX}-${GIT_MARKER}-${PROJECT_NAME}-${BUILD_ID_FILE}"
  if [[ "${USE_FILE}" == "true" ]]; then
    local TARGET_ID="none"
    getBuildIdFromFile TARGET_ID ${ID_FILE}
    FINAL_ID="${TARGET_ID}"
  else
    FINAL_ID="${PROJECT_NAME}:${BUILD_ID}"
  fi
  echo ""
  echo "Checking build ${FINAL_ID}"
  aws codebuild batch-get-builds --ids ${FINAL_ID} | jq --raw-output '.builds[] | { id: .id, currentPhase: .currentPhase, buildStatus: .buildStatus, startTime: .startTime, endTime: .endTime, location: .artifacts.location } '
  echo ""
}

function listBuilds () {
  local PROJECT_NAME=${1}
  aws codebuild list-builds-for-project --project-name ${PROJECT_NAME} --sort-order ASCENDING
}

$@

