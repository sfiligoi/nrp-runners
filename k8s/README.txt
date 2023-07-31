Runner in NRP k8s files
=======================

For each namespace:

1) Create necessary service account
kubectl create -n biocore-build -f k8s-account.yaml 

2) Get a github token
(https://github.com/settings/tokens?type=beta)
and save the content in github_token.txt.

Then create the necessary k8s secret:
kubectl create secret generic -n biocore-build nrp-runner-token --from-file=github_token.txt

Note: If the token needs to be updated, use:
kubectl create secret generic -n biocore-build nrp-runner-token --from-file=github_token.txt --save-config --dry-run=client -o yaml | kubectl apply -f -

3) Create PVC
Note: You can share the PVC among many github repositories,
      if they share the nsame NRP namespace:

kubectl create -n <namespace> -f pvc.yaml


For each githup repository:

4) Setup the runner.
Get one-time token from github
https://github.com/<project>/<repo>/settings/actions/runners

kubectl create -n <namespace> -f setup_pod.yaml 
# wait for the pod to start
kubectl exec -n <namespace> -it setup-interactive -- /opt/init_runner.sh <project> <repo> <token> linux-gpu-cuda nrp-linux-gpu-cuda
kubectl delete -n <namespace> -f setup_pod.yaml

5) Launch the runner deployment, without any running pods as the default

kubectl create -n <namespace> -f <repo>/runner_deployment.yaml

6) Launch the runner manager
kubectl create -n <namespace> -f <repo>/runner_manager.yaml


