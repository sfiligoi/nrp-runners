FROM ubuntu:22.04

RUN apt-get update

RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install --yes python3 python3-kubernetes python3-pycurl

ADD scripts/runner_manager.py /opt/runner_manager.py
RUN chmod a+x /opt/runner_manager.py

