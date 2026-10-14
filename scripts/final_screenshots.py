from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':1100})
 for name,url in [('github-public-gate','https://github.com/YangKeao/security-alternatives-public-lab-20261014/pull/1'),('github-public-release','https://github.com/YangKeao/security-alternatives-public-lab-20261014/releases/tag/lab-public-rc1-8.5'),('github-report-entry','https://github.com/YangKeao/security-alternatives-public-lab-20261014/security/advisories')]:
  page.goto(url,wait_until='domcontentloaded',timeout=60000);page.wait_for_timeout(1000);page.screenshot(path=str(R/'screenshots'/(name+'.png')),full_page=True);print(name,page.title(),flush=True)
 b.close()
