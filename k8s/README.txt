Runner in NRP k8s files
=======================

You can share the PVC among many github repositories,
if they share the nsame NRP namespace:

1) Create PVC
kubectl create -n <namespace> -f pvc.yaml

Fr each githup repository:

2) Setup the runner.
Get one-time token from github
https://github.com/<project>/<repo>/settings/actions/runners

kubectl create -n <namespace> -f setup_pod.yaml 
kubectl exec -n <namespace> -it setup-interactive -- /bin/bash
# as root inside the pod
mkdir /mnt/persistent/builder
chown builder /mnt/persistent/builder
su - builder
# you are now the builder user, never use root again
cd /mnt/persistent/builder
mkdir <repo>
cd <repo> 
tar -xzf /opt/downloads/actions-runner-linux.tar.gz 
./config.sh --url https://github.com/<project>/<repo> --token <token> --labels linux-gpu-cuda --name nrp-linux-gpu-cuda --work /mnt/scratch/builder 
# exit the pod

kubectl delete -n <namespace> -f setup_pod.yaml

3) Launch the runner deployment, without any running pods as the default

kubectl create -n <namespace> -f <repo>/runner_deployment.yaml

4) Launch the runner manager
TBD

