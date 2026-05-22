Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   Bootstrapping Valkyrie Platform       " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Create k3d cluster
Write-Host "[1/6] Creating k3d cluster 'valkyrie-platform'..." -ForegroundColor Yellow
k3d cluster create valkyrie-platform --agents 2 -p "8080:80@loadbalancer" -p "8443:443@loadbalancer"

# 2. ArgoCD
Write-Host "[2/6] Installing ArgoCD..." -ForegroundColor Yellow
kubectl create namespace argocd
kubectl apply --server-side --force-conflicts -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 3. Observability
Write-Host "[3/6] Installing Prometheus and Grafana..." -ForegroundColor Yellow
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring

# 4. Loki
Write-Host "[4/6] Installing Loki..." -ForegroundColor Yellow
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install loki grafana/loki-stack -n monitoring

# 5. Falco
Write-Host "[5/6] Installing Falco..." -ForegroundColor Yellow
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update
kubectl create namespace falco
helm install falco falcosecurity/falco -n falco

# 6. Litmus & Sample App
Write-Host "[6/6] Installing Litmus Chaos and Sample App..." -ForegroundColor Yellow
kubectl create namespace litmus
kubectl apply -f https://litmuschaos.github.io/litmus/litmus-operator-v3.0.0.yaml
kubectl apply -f W:\Projects\Web-Starter\Valkarie_Platform_local\apps\sample-app\deployment.yaml

Write-Host "`nBootstrap Complete!" -ForegroundColor Green
Write-Host "To start the UIs, run .\scripts\start-valkyrie.ps1"
