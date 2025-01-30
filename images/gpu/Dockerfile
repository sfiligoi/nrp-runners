FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install --yes curl openssh-client make gcc gfortran gfortran python-is-python3 environment-modules 

RUN mkdir /opt/downloads && cd /opt/downloads && \
    curl -o actions-runner-linux-x64-2.321.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-linux-x64-2.321.0.tar.gz && \
    ln -s actions-runner-linux-x64-2.321.0.tar.gz actions-runner-linux.tar.gz 

RUN mkdir /opt/actions-runner && cd /opt/actions-runner && \
    tar -xzf /opt/downloads/actions-runner-linux.tar.gz

RUN cd /opt/actions-runner && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC ./bin/installdependencies.sh
    
RUN useradd -m -s /bin/bash builder

# initialization scripts
ADD support/init_runner.sh /opt/init_runner.sh
ADD support/init_runner_builder.sh /opt/init_runner_builder.sh

# main run script
ADD support/run_runner.sh /opt/run_runner.sh

RUN chmod a+x /opt/init_runner.sh && chmod a+x /opt/init_runner_builder.sh && chmod a+x /opt/run_runner.sh

