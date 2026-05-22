param (
    [switch]$AI = $false
)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   Starting Valkyrie Platform Services   " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Port-forward ArgoCD
Write-Host "[1/3] Starting ArgoCD Port-Forward on https://localhost:8081..." -ForegroundColor Yellow
$cmd1 = "`$env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine') + ';'+ [System.Environment]::GetEnvironmentVariable('Path', 'User'); kubectl port-forward svc/argocd-server -n argocd 8081:443"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd1 -WindowStyle Minimized

# 2. Port-forward Grafana
Write-Host "[2/3] Starting Grafana Port-Forward on http://localhost:3000..." -ForegroundColor Yellow
$cmd2 = "`$env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine') + ';'+ [System.Environment]::GetEnvironmentVariable('Path', 'User'); kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 3000:80"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd2 -WindowStyle Minimized

# 3. Start AI Incident Engine (Optional)
if ($AI) {
    Write-Host "[3/3] Installing requirements and Starting AI Incident Engine on http://localhost:8000..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd W:\Projects\Web-Starter\Valkarie_Platform_local\ai-engine\api; pip install -r requirements.txt; uvicorn main:app --reload --port 8000" -WindowStyle Normal
} else {
    Write-Host "[3/3] Skipping AI Engine. Run with -AI `$true to start it." -ForegroundColor DarkGray
}

$ARGO_PASS = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}")))
$GRAFANA_PASS = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((kubectl -n monitoring get secrets kube-prometheus-stack-grafana -o jsonpath="{.data.admin-password}")))

Write-Host "`nAll services started in background windows!" -ForegroundColor Green
Write-Host "-----------------------------------------"
Write-Host "ArgoCD UI : https://localhost:8081"
Write-Host "   User   : admin"
Write-Host "   Pass   : $ARGO_PASS"
Write-Host "-----------------------------------------"
Write-Host "Grafana UI: http://localhost:3000"
Write-Host "   User   : admin"
Write-Host "   Pass   : $GRAFANA_PASS"
Write-Host "-----------------------------------------"
Write-Host "To run a Chaos test, open a new terminal and run:"
Write-Host "kubectl apply -f .\chaos\litmus\pod-delete.yaml" -ForegroundColor Magenta
Write-Host "========================================="
