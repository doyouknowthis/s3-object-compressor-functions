#!/bin/bash

zip_layer() {
  local function_name=$1
  local function_suffix=${2:-latest}

  if [ -z "$function_name" ]; then
    echo "Function name not provided"
    exit 1
  fi

  # echo "Deleting initial directories"
  rm -rdf python/
  rm -f "${function_name}-layer-${function_suffix}.zip"

  cd "src/functions/$function_name/" || return
  pip install -r requirements.txt -t python
  zip -r "${function_name}-layer-${function_suffix}" python/
  mv "${function_name}-layer-${function_suffix}.zip" ../../..

  # echo "Deleting \"python\" directory"
  rm -rdf python/
}

zip_layer "$1" "$2"