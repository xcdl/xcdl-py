#! /bin/bash

# The relative position of the folder where the Python code is located.
# In this case it is just around the corner, in the src folder.
# Change it only if you decide to reorganise folders and move the scripts 
# to another location.

RELATIVE_SRC_PATH=../src

# Get absolute path of shell script. Supports:
# source ./script (When called by the . dot operator)
# Absolute path /path/to/script
# Relative path like ./script
# /path/dir1/../dir2/dir3/../script
# When called from symlink
# When symlink is nested eg) foo->dir1/dir2/bar bar->./../doe doe->script
# When caller changes the scripts name

pushd . > /dev/null
SCRIPT_PATH="${BASH_SOURCE[0]}";
  while([ -h "${SCRIPT_PATH}" ]) do 
    cd "`dirname "${SCRIPT_PATH}"`"
    SCRIPT_PATH="$(readlink "`basename "${SCRIPT_PATH}"`")"; 
  done
cd "`dirname "${SCRIPT_PATH}"`" > /dev/null
SCRIPT_PATH="`pwd`";
popd  > /dev/null
#echo "script=[${SCRIPT_PATH}]"
#echo "pwd   =[`pwd`]"

export PYTHONPATH=$PYTHONPATH:$SCRIPT_PATH/$RELATIVE_SRC_PATH

python -m ilg.xcdl.configMakefiles "$@"
