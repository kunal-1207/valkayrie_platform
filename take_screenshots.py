import os
import time
import base64
import subprocess
from playwright.sync_api import sync_playwright

def get_secret(namespace, secret_name, jsonpath):
    cmd = f'kubectl -n {namespace} get secret {secret_name} -o jsonpath="{{{jsonpath}}}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to fetch secret: {result.stderr}")
    return base64.b64decode(result.stdout.strip()).decode('utf-8')

def main():
    print("Fetching passwords...")
    try:
        argo_pass = get_secret("argocd", "argocd-initial-admin-secret", ".data.password")
        grafana_pass = get_secret("monitoring", "kube-prometheus-stack-grafana", ".data.admin-password")
    except Exception as e:
        print(f"Error fetching passwords: {e}")
        return

    print("Starting port forwards...")
    pf_argo = subprocess.Popen("kubectl port-forward svc/argocd-server -n argocd 8081:443", shell=True)
    pf_grafana = subprocess.Popen("kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 3000:80", shell=True)
    
    time.sleep(5) # Wait for ports to open

    os.makedirs("screenshots", exist_ok=True)

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True, viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            print("Capturing ArgoCD...")
            page.goto("https://localhost:8081/login", timeout=15000)
            page.fill("input[id='username']", "admin")
            page.fill("input[id='password']", argo_pass)
            page.click("button[type='submit']")
            page.wait_for_url("**/applications")
            
            # Navigate to sample-app
            page.goto("https://localhost:8081/applications/argocd/sample-app?view=network&resource=", timeout=15000)
            time.sleep(5) # wait for graph to render
            page.screenshot(path="screenshots/argocd.png")
            print("ArgoCD screenshot saved.")
        except Exception as e:
            print(f"Failed ArgoCD: {e}")

        try:
            print("Capturing Grafana...")
            page.goto("http://localhost:3000/login", timeout=15000)
            page.fill("input[name='user']", "admin")
            page.fill("input[name='password']", grafana_pass)
            page.click("button[type='submit']")
            page.wait_for_url("**/")
            
            # Navigate to a cool dashboard
            page.goto("http://localhost:3000/d/85a562078cdf77779eaa1add43ccec1e/kubernetes-compute-resources-namespace-pods?orgId=1&var-namespace=sample-app", timeout=15000)
            time.sleep(5) # wait for panels to load
            page.screenshot(path="screenshots/grafana.png")
            print("Grafana screenshot saved.")
        except Exception as e:
            print(f"Failed Grafana: {e}")

        browser.close()

    print("Cleaning up...")
    pf_argo.kill()
    pf_grafana.kill()
    print("Done!")

if __name__ == "__main__":
    main()
