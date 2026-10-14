import jenkins.model.Jenkins
import hudson.security.HudsonPrivateSecurityRealm
import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import groovy.json.JsonSlurper
Jenkins j = Jenkins.get()
def auth = new JsonSlurper().parse(new File('/lab/.secrets/lab-auth.json'))
def realm = new HudsonPrivateSecurityRealm(false)
realm.createAccount('labadmin', auth.jenkins_admin_password)
j.setSecurityRealm(realm)
def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
strategy.setAllowAnonymousRead(false)
j.setAuthorizationStrategy(strategy)
j.setNumExecutors(1)
j.save()
