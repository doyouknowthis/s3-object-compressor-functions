#!/bin/bash

zip_function() {
  local function_name=$1
  local function_suffix=${2:-latest}
  local tmp_folder="functions"
  local zip_folder=$function_name

  if [ -z "$function_name" ]; then
    echo "Function name not provided"
    exit 1
  fi

  # echo "Deleting initial directories"
  rm -rdf "${tmp_folder:?}/"

  echo "Zipping function \"$function_name\""

  mkdir -p "$tmp_folder/"
  cp "src/functions/common.py" "src/functions/__init__.py" "$tmp_folder/"
  cp -r "src/functions/$function_name/" "$tmp_folder/$function_name"
  zip -r "$zip_folder-$function_suffix" "$tmp_folder/"

  # echo "Deleting directory $dest_folder/", keep zip
  rm -rdf "${tmp_folder:?}/"
}

zip_function "$1" "$2"