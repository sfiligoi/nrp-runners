FROM nvidia/cuda:11.7.1-devel-ubuntu20.04

RUN apt-get update && apt-get install --yes curl

RUN curl -o actions-runner-linux-x64-2.299.1.tar.gz -L https://github.com/actions/runner/releases/download/v2.299.1/actions-runner-linux-x64-2.299.1.tar.gz && \
    ln -s actions-runner-linux-x64-2.299.1.tar.gz actions-runner-linux.tar.gz 

