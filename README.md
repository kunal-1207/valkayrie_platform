# Valkyrie Platform 

**A Production-Grade, Local-First Kubernetes Platform**

Valkyrie is an autonomous DevOps platform designed to run entirely locally (zero cloud burn) while maintaining enterprise-grade architectural standards. It integrates GitOps, centralized observability, AI-driven incident analysis, DevSecOps, chaos engineering, and a unified developer portal.

---

## 🏗 Architecture

The platform runs on a local Kubernetes cluster powered by `k3d` and Docker Desktop.

- **Container Runtime & Cluster:** Docker Desktop + `k3d` (3-node cluster)
- **GitOps:** ArgoCD
- **Observability Stack:** Prometheus, Grafana, Loki
- **Security:** Falco (Runtime Security)
- **Chaos Engineering:** LitmusChaos
- **AI Incident Engine:** Custom FastAPI Service + Ollama LLM
- **Developer Portal:** Backstage

---

## 🚀 Quick Start Guide

### 1. Bootstrap the Infrastructure
If you haven't already built the cluster, run the automated bootstrap script. This will provision the `k3d` cluster and install all Helm charts and manifests automatically:
```powershell
.\scripts\bootstrap.ps1
```

### 2. Start the Services
To expose the internal cluster UIs to your host machine and start the AI engine, run the startup script:
```powershell
.\scripts\start-valkyrie.ps1 -AI $true
```

### 3. Access the Portals
- **ArgoCD:** [https://localhost:8081](https://localhost:8081) *(User: `admin` | Pass: `37NaPXEElaGkZfJ0`)*
- **Grafana:** [http://localhost:3000](http://localhost:3000) *(User: `admin` | Pass: `VZyWFBSTBRIW3HZ90glmjIr4c2WrhZwRBaGVGrlX`)*

---

## 🧪 Testing & Verification (CLI Screenshots)

Below are the native CLI captures proving the operational status of the cluster components during testing.

### 1. Cluster Nodes
```text
NAME                             STATUS   ROLES                  AGE   VERSION
k3d-valkyrie-platform-agent-0    Ready    <none>                 23m   v1.31.5+k3s1
k3d-valkyrie-platform-agent-1    Ready    <none>                 23m   v1.31.5+k3s1
k3d-valkyrie-platform-server-0   Ready    control-plane,master   23m   v1.31.5+k3s1
```

### 2. GitOps (ArgoCD)
```text
NAME                                                READY   STATUS    RESTARTS   AGE
argocd-application-controller-0                     1/1     Running   0          23m
argocd-applicationset-controller-6fb45499bf-fhg8p   1/1     Running   0          23m
argocd-dex-server-5f969b9b4d-x9rnk                  1/1     Running   0          23m
argocd-notifications-controller-5d488dc9dd-w7l22    1/1     Running   0          23m
argocd-redis-59f4c5f58b-njs6v                       1/1     Running   0          23m
argocd-repo-server-84788d4897-5sjgn                 1/1     Running   0          23m
argocd-server-6856fd4959-xfdd2                      1/1     Running   1          23m
```

### 3. Security (Falco)
```text
NAME          READY   STATUS    RESTARTS   AGE
falco-jbqdx   2/2     Running   0          17m
falco-khdmk   2/2     Running   0          17m
falco-rh2cf   2/2     Running   0          17m
```

### 4. Sample Workload 
```text
NAME                        READY   STATUS    RESTARTS   AGE
backend-b59d76759-vvjpt     1/1     Running   0          17m
frontend-5dc596f66c-tj26d   1/1     Running   0          17m
redis-6664db5d7c-5xq8k      1/1     Running   0          17m
```

### 5. Chaos Engineering (Litmus)
```text
NAME                                 READY   STATUS    RESTARTS   AGE
chaos-operator-ce-78c4464799-dnp89   1/1     Running   1          17m
```

---

## 🌪 Running a Chaos Experiment

To test cluster resilience and observe auto-healing, trigger a chaos experiment:
```powershell
kubectl apply -f .\chaos\litmus\pod-delete.yaml
```
*Monitor the Grafana dashboards and Falco logs to observe the incident detection and auto-recovery process.*
