#!/usr/bin/python3

import sys
import time
import pycurl
from io import BytesIO
import json
import kubernetes

# will base policy on my start time
# that will randomize a bit the distributon if we have multiple processes
my_start_time=time.time()

def getruns(who,state,token):
    try:
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://api.github.com/repos/%s/actions/runs?status=%s'%(who,state))
        if token is not None:
            headers=("Accept: application/vnd.github+json","Authorization: Bearer %s"%token)
            c.setopt(pycurl.HTTPHEADER, headers)
        buffer = BytesIO()
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
    except:
        print("%s Failed to contact github"%time.ctime(), flush=True)
        return None

    try:
        body = buffer.getvalue().decode('ascii')
        doc=json.loads(body)
        cnt=doc['total_count']
        return cnt
    except:
        pass
    # if we got here, there was an error
    try:
        errmsg=doc['message']
        print("%s Github error: %s"%(time.ctime(), errmsg), flush=True)
        return None
    except:
        # OK, I give up
        print("%s GitHub Parsing error!"%time.ctime(), flush=True)
        return None

    return cnt

def getqueuedruns(who,token):
    return getruns(who,"queued",token)

def getactiveruns(who,token):
    return getruns(who,"in_progress",token)

def getrunners(nmspace,repo):
    try:
        k8s = kubernetes.client.AppsV1Api()
        dlist = k8s.list_namespaced_deployment(namespace=nmspace,label_selector="runner-repo=%s"%repo)
    except:
        print("%s Failed to contact k8s"%time.ctime(), flush=True)
        return None

    try:
        if len(dlist.items)<1:
           print("%s Cannot find deployment runner-repo=%s"%(time.ctime(),repo), flush=True)
           return None
        nm = dlist.items[0].metadata.name
        cnt = dlist.items[0].spec.replicas
    except:
        print("%s K8S Parsing error!"%time.ctime(), flush=True)
        return None

    return (nmspace,nm,cnt)

def setrunners(nmspace, nm, cnt):
    try:
        k8s = kubernetes.client.AppsV1Api()
        k8s.patch_namespaced_deployment(namespace=nmspace,name=nm, body={'spec': {'replicas': cnt}})
    except:
        print("%s Deployment update failed"%time.ctime(), flush=True)

in_periodic=False

# keep one runner alive only if there are any waiting runs
# except for periodic intervals needed to keep the token alive
#  awake_period is the frequency with a default of 3 days (tokens are valid of a week)
#  awak_length is the time to stay awak, default just over 33 mins to allow for binary updates
def checkandsetrunners(nmspace, who, repo, token, awake_period=250000, awake_length=2000):
    # find how many runners we already have
    runner_cnt_arr = getrunners(nmspace,repo)
    if runner_cnt_arr is None:  # Error detected, just bail
       return

    runner_cnt = runner_cnt_arr[2]

    alive_secs=int(time.time()-my_start_time)
    awake_point = alive_secs%awake_period

    if awake_point<awake_length:
       if runner_cnt==0:
          # force one alive runniner during the awake period
          print("%s Starting periodic runner %s"%(time.ctime(), repo), flush=True)
          setrunners(runner_cnt_arr[0], runner_cnt_arr[1], 1)
       # else just make sure it stays that way
       in_periodic=True
       return

    # else, use the normal logic

    # find how many jobs are in neeed of a runner
    run_cnt = getqueuedruns(who,token)
    if run_cnt is None: # Error detected
       if (in_periodic):
           # if in the periodic setup, stop it, we likely don't need it
           print("%s Stopping periodic runner %s"%(time.ctime(), repo), flush=True)
           setrunners(runner_cnt_arr[0], runner_cnt_arr[1], 0)
           n_periodic=False
       # bail, keep the current status, there may be active runs in progress
       return

    in_periodic=False
    if runner_cnt==0:
       if run_cnt>0:
         print("%s Starting runner %s"%(time.ctime(), repo), flush=True)
         setrunners(runner_cnt_arr[0], runner_cnt_arr[1], 1)
    else:
       run_cnt2 = getactiveruns(who,token)
       if run_cnt2 is None:
          return
       if (run_cnt+run_cnt2)<1:
         print("%s Stopping runner %s"%(time.ctime(), repo), flush=True)
         setrunners(runner_cnt_arr[0], runner_cnt_arr[1], 0)

def main(nmspace, who, repo, stime):
    kubernetes.config.load_incluster_config()
    with open("/etc/github_token.txt","r") as fd:
        token=fd.readlines()[0].strip()

    print("%s Manager args %s,%s,%s,%s"%(time.ctime(), nmspace, who, repo, stime), flush=True)
    while True: #run forever
      checkandsetrunners(nmspace, who, repo, token)
      time.sleep(stime)

if __name__ == '__main__':
   main(sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]))



