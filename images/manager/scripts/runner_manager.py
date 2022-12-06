#!/usr/bin/python3

import sys
import time
import pycurl
from io import BytesIO
import json
import kubernetes

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
        print("Failed to contact github")
        return None

    try:
        body = buffer.getvalue().decode('ascii')
        doc=json.loads(body)
        cnt=doc['total_count']
    except:
        print("Parsing error!")
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
        print("Failed to contact k8s")
        return None

    try:
        if len(dlist.items)<1:
           print("Cannot find deployment runner-repo=%s"%repo)
           return None
        nm = dlist.items[0].metadata.name
        cnt = dlist.items[0].spec.replicas
    except:
        print("Parsing error!")
        return None

    return (nmspace,nm,cnt)

def setrunners(nmspace, nm, cnt):
    try:
        k8s = kubernetes.client.AppsV1Api()
        k8s.patch_namespaced_deployment(namespace=nmspace,name=nm, body={'spec': {'replicas': cnt}})
    except:
        print("Deployment update failed")

# keep one runner alive only if there are any waiting runs
def checkandsetrunners(nmspace, who, repo, token):
    run_cnt = getqueuedruns(who,token)
    if run_cnt is None:
       return
    runner_cnt_arr = getrunners(nmspace,repo)
    if runner_cnt_arr is None:
       return

    runner_cnt = runner_cnt_arr[2]

    if runner_cnt==0:
       if run_cnt>0:
         print("%s Starting runner %s"%(time.ctime(), repo))
         setrunners(runner_cnt_arr[0], runner_cnt_arr[1], 1)
    else:
       run_cnt2 = getactiveruns(who,token)
       if run_cnt2 is None:
          return
       if (run_cnt+run_cnt2)<1:
         print("%s Stopping runner %s"%(time.ctime(), repo))
         setrunners(runner_cnt_arr[0], runner_cnt_arr[1], 0)

def main(nmspace, who, repo, stime):
    kubernetes.config.load_incluster_config()
    with open("/etc/github_token.txt","r") as fd:
        token=fd.readlines()[0].strip()

    print("%s Manager args %s,%s,%s,%s"%(time.ctime(), nmspace, who, repo, stime))
    while True: #run forever
      checkandsetrunners(nmspace, who, repo, token)
      time.sleep(stime)

if __name__ == '__main__':
   main(sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]))



