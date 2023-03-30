#!/bin/bash
if [ -n /mnt/persistent/builder ]; then 
  mkdir -p /mnt/persistent/builder
  chown builder /mnt/persistent/builder
fi

if [ -n /mnt/scratch/builder ]; then 
  mkdir -p /mnt/scratch/builder
  chown builder /mnt/scratch/builder
fi

su - builder -c "/opt/init_runner_builder.sh $1 $2 $3 $4 $5"

