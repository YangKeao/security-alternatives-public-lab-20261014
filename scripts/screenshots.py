from playwright.sync_api import sync_playwright
from pathlib import Path
import json,base64
R=Path(__file__).resolve().parents[1];auth=json.load(open(R/'.secrets/lab-auth.json'))
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1050})
 for name,url in [('github-public-repo','https://github.com/YangKeao/security-alternatives-public-lab-20261014'),('github-private-anonymous','https://github.com/YangKeao/security-embargo-private-lab-20261014')]:
  page.goto(url,wait_until='domcontentloaded',timeout=60000);page.wait_for_timeout(1500);page.screenshot(path=str(R/'screenshots'/(name+'.png')),full_page=True);print(name,page.title(),flush=True)
 context=b.new_context(viewport={'width':1440,'height':1050},extra_http_headers={'Authorization':'Basic '+base64.b64encode(('labadmin:'+auth['jenkins_admin_password']).encode()).decode()});page=context.new_page()
 for num in [1,2,3,5]:
  page.goto(f'http://127.0.0.1:18981/job/synthetic-embargo/{num}/',wait_until='domcontentloaded');page.wait_for_timeout(500);page.screenshot(path=str(R/'screenshots'/f'jenkins-build-{num}.png'),full_page=True);print('jenkins',num,page.title(),flush=True)
 page.goto('http://127.0.0.1:18981/job/synthetic-embargo/5/console',wait_until='domcontentloaded');page.screenshot(path=str(R/'screenshots'/'jenkins-real-webhook-console.png'),full_page=True)
 b.close()
