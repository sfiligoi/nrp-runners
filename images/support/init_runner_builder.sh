#!/bin/bash
if [ -n /mnt/persistent/builder/$2 ]; then 
   cd /mnt/persistent/builder
   mkdir "$2" && cd "$2" && tar -xzf /opt/downloads/actions-runner-linux.tar.gz 
   ./config.sh --url "https://github.com/$1/$2" --token "$3" --labels "$4" --name "$5" --work /mnt/scratch/builder 
fi
