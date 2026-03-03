# Incident Response Plan

Procedures for detecting, responding to, and recovering from security incidents.

## Table of Contents
- [Incident Types](#incident-types)
- [Response Procedures](#response-procedures)
- [Communication Plan](#communication-plan)
- [Investigation Checklist](#investigation-checklist)
- [Recovery Procedures](#recovery-procedures)
- [Post-Incident Review](#post-incident-review)
- [Contact Information](#contact-information)

---

## Incident Types

### Critical Incidents

**Data Breach** - Unauthorized access to financial data
- **Action**: Immediate escalation to security team
- **Timeline**: Notification within 4 hours

**Ransomware** - System encrypted by attacker
- **Action**: Isolate systems, contact law enforcement
- **Timeline**: Immediate shutdown of affected systems

**System Compromise** - Unauthorized system access
- **Action**: Kill attacker connections, preserve evidence
- **Timeline**: 1-hour containment target

### High Priority

**Unauthorized Access** - Failed attempt or brief access
- **Action**: Reset credentials, review logs
- **Timeline**: 8-hour investigation

**Data Loss** - Accidental deletion or corruption
- **Action**: Restore from backup, verify integrity
- **Timeline**: 24-hour recovery target

### Medium Priority

**Vulnerability Discovery** - Security flaw found
- **Action**: Develop patch, schedule deployment
- **Timeline**: 48-hour patch development

**Policy Violation** - Non-compliance with security policy
- **Action**: Document, remediate, educate
- **Timeline**: 1-week remediation

### Low Priority

**Security Warning** - Potential issue detected
- **Action**: Monitor, log, schedule review
- **Timeline**: Next maintenance window

---

## Response Procedures

### Incident Severity Assessment Matrix

| Severity | Data Exposed | Systems Down | Users Affected | Response Time |
|----------|--------------|--------------|----------------|---------------|
| **Critical** | Yes, sensitive | All/core | All | 15 minutes |
| **High** | Yes, limited | Some | Some | 1 hour |
| **Medium** | No | One | Few | 4 hours |
| **Low** | No | Test only | None | 24 hours |

### Step 1: Detection & Reporting

```
Anyone discovering a potential security incident should:

1. DO NOT attempt to fix it yourself
2. DO NOT delete or modify evidence
3. Document what you observed:
   - What happened?
   - When did you notice it?
   - What systems/data affected?
   - Is it still happening?
4. Report immediately to security team email:
   security@yourdomain.com
5. If urgent, also call: [PHONE NUMBER]
```

### Step 2: Triage & Containment

**Immediately (0-15 minutes):**

```bash
# Determine severity
echo "Critical? (Y/N): "
if [[ $severity == "Y" ]]; then
    # CRITICAL PROCEDURE
    
    # 1. Kill attacker connection (if network access)
    sudo fail2ban-client set sshd banip 192.168.x.x
    
    # 2. Stop web service
    sudo systemctl stop financial-api
    
    # 3. Isolate database
    # Take database offline if needed
    
    # 4. Preserve evidence
    sudo tar -czf /evidence/logs-$(date +%s).tar.gz /var/log
    
    # 5. Alert management
    # Send emergency notification to incident commander
fi
```

**Within 1 hour:**

```bash
# Containment actions
1. Isolate affected systems from network (if necessary)
2. Block attacker IP addresses
3. Reset compromised credentials
4. Enable enhanced monitoring
5. Collect and preserve logs
6. Document timeline
```

### Step 3: Investigation

Use the investigation checklist below. Key questions:

- **What**: What was compromised/affected?
- **When**: When did it start? When was it discovered?
- **Who**: Who had access? Who could have done this?
- **How**: How was access gained? What was the attack vector?
- **Why**: What was the attacker trying to achieve?
- **Where**: What systems/data were accessed?
- **Scope**: How much data exposed? How many systems?

### Step 4: Eradication

```bash
# Remove attacker access
1. Change all compromised credentials
2. Patch vulnerable systems
3. Remove malware/backdoors
4. Update firewall rules
5. Verify system integrity

# Validation
1. Run security scans
2. Check for persistence mechanisms
3. Verify clean system baseline
4. Test system functionality
```

### Step 5: Recovery

```bash
# Bring systems back online safely
1. Verify clean backup exists
2. Test backup recovery on staging
3. Plan maintenance window
4. Restore from clean backup
5. Update systems
6. Bring online incrementally
7. Verify functionality
8. Monitor for issues
```

### Step 6: Post-Incident

```bash
# After resolution
1. Complete Root Cause Analysis
2. Identify preventive measures
3. Update security controls
4. Document lessons learned
5. Update runbooks/procedures
6. Conduct team debrief
7. Implement improvements
```

---

## Communication Plan

### Notification Priority

**Immediately notify (within 1 hour):**
- Security team
- System administrator
- Management/Incident Commander

**Within 24 hours (if data breach):**
- Legal team
- Compliance officer
- Affected users
- Authorities (if required)

### Notification Template

```
Subject: URGENT - Security Incident [INCIDENT_ID] - [SEVERITY]

Incident Details:
- ID: [Auto-generated ID]
- Type: [Breach/Outage/Unauthorized Access/etc]
- Severity: [Critical/High/Medium/Low]
- Discovered: [Date/Time UTC]
- Reported By: [Name]

What Happened:
[Clear description of incident]

Systems Affected:
- [System 1]
- [System 2]

Data Exposure:
- Type: [Financial data/User data/Other]
- Records: [Estimated number]
- Sensitive Info: [What was exposed]

Current Status:
- [Contained/Investigating/Resolved]
- [Actions taken so far]

Next Steps:
- [Planned actions]
- [Timeline]

Contact:
- Incident Commander: [Name] [Phone/Email]
- Security Lead: [Name] [Phone/Email]
```

### Internal Communication

```
Team Slack Channel: #security-incidents

[Every 2 hours during active incident]
Status Update: [What we've done, current status, next steps]

[Every 24 hours during investigation]
Investigation Update: [Findings, actions, timeline]
```

---

## Investigation Checklist

### Incident Evidence Preservation

```bash
# Preserve evidence IMMEDIATELY
# DO NOT clean/restart systems

# 1. Capture system state
sudo ps aux > evidence/processes-$(date +%s).txt
sudo netstat -tulnap > evidence/connections-$(date +%s).txt
sudo cat /proc/*/environ | tr '\0' '\n' > evidence/environment-$(date +%s).txt

# 2. Collect logs
sudo tar -czf evidence/var-log-$(date +%s).tar.gz /var/log
sudo tar -czf evidence/app-logs-$(date +%s).tar.gz /app/logs

# 3. Database backup
pg_dump -U postgres financial_analysis > evidence/db-backup-$(date +%s).sql

# 4. Memory dump (if live forensics needed)
sudo dd if=/dev/mem of=evidence/memory-dump-$(date +%s).bin
```

### System Analysis

```
□ Review system logs for suspicious activity
  - Failed login attempts
  - Privilege escalation
  - Unusual processes
  - Network connections

□ Check user accounts
  - New accounts created?
  - Account modifications?
  - Privilege changes?
  - SSH keys added?

□ Verify file integrity
  - Modified system files?
  - New files created?
  - Deleted files?
  - Permission changes?

□ Network analysis
  - Unusual traffic patterns?
  - Connections to suspicious IPs?
  - Data exfiltration?
  - DDoS activity?

□ Application logs
  - Error messages?
  - Access patterns?
  - Failed operations?
  - API abuse?

□ Database changes
  - Schema modifications?
  - Data deletions?
  - Access patterns?
  - Backup integrity?
```

### Financial Data Exposure Assessment

```
If financial data potentially exposed, determine:

□ What data was accessed?
  □ Account numbers
  □ Transaction history
  □ Personal information
  □ Authentication credentials

□ How much data?
  □ Number of accounts
  □ Number of records
  □ Time period covered

□ How long was access possible?
  □ Start date
  □ End date
  □ Duration

□ Who could have accessed it?
  □ Direct access via vulnerability
  □ Through compromised credentials
  □ Through third-party breach
  □ Unknown exposure vector

□ Was it actually exfiltrated?
  □ Log evidence of data access
  □ Network traffic analysis
  □ Database query logs
  □ File access logs
```

---

## Recovery Procedures

### Database Recovery

```bash
# 1. Stop application
sudo systemctl stop financial-api

# 2. Verify backup integrity
pg_restore --list database-backup.sql | head -20

# 3. Create new database for restore test
createdb financial_analysis_restore_test
pg_restore -d financial_analysis_restore_test database-backup.sql

# 4. Verify restored data
psql -d financial_analysis_restore_test -c "SELECT COUNT(*) FROM api_transaction;"

# 5. If valid, proceed with production restore
createdb financial_analysis_new
pg_restore -d financial_analysis_new database-backup.sql

# 6. Verify production restore
psql -d financial_analysis_new -c "SELECT COUNT(*) FROM api_transaction;"

# 7. Point application to new database
# Update DATABASE_URL
export DATABASE_URL=postgresql://user:pass@host/financial_analysis_new

# 8. Run migrations
python manage.py migrate

# 9. Verify application functionality
curl http://localhost:8000/api/institutions/

# 10. Start application
sudo systemctl start financial-api

# 11. Monitor for issues
tail -f /var/log/django/app.log
```

### Credential Reset

```bash
# Reset Django superuser password
python manage.py changepassword admin

# Generate new SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Update all API keys
# Update all database passwords
# Rotate all certificates
# Reset all tokens
```

---

## Post-Incident Review

### Root Cause Analysis Template

```markdown
# Incident Post-Mortem: [INCIDENT_ID]

## Executive Summary
[2-3 sentence overview of incident and impact]

## Timeline
- [Time 1]: Event happened
- [Time 2]: Detected
- [Time 3]: Action taken
- [Time 4]: Resolved

## Impact
- Data exposed: [Yes/No], [Amount]
- Users affected: [Number]
- Systems down: [Duration]
- Business impact: [Description]

## Root Cause
[What caused the incident?]

## Contributing Factors
- [Factor 1]
- [Factor 2]
- [Factor 3]

## What Went Well
- [Good response]
- [Good communication]
- [Good containment]

## What Could Be Better
- [Improvement 1]
- [Improvement 2]
- [Improvement 3]

## Action Items
1. [Action] - Owner: [Name] - Due: [Date]
2. [Action] - Owner: [Name] - Due: [Date]
3. [Action] - Owner: [Name] - Due: [Date]

## Prevention
[How will we prevent this in the future?]

## Monitoring
[What monitoring/alerts will we add?]
```

### Lessons Learned

```bash
# Document for team
1. What happened?
2. Why did it happen?
3. What did we do right?
4. What could we improve?
5. How do we prevent it?

# Share knowledge
- Team meeting to review
- Update runbooks/procedures
- Update security documentation
- Training on lessons learned
```

---

## Contact Information

### Incident Escalation

```
Level 1: Security Team (on-call)
- Email: security@yourdomain.com
- Phone: +1-XXX-XXX-XXXX
- Available: 24/7 on-call rotation

Level 2: Security Manager
- Email: security.manager@yourdomain.com
- Phone: +1-XXX-XXX-XXXX

Level 3: CISO/Executive
- Email: ciso@yourdomain.com
- Phone: +1-XXX-XXX-XXXX

Level 4: Legal & Compliance
- Email: legal@yourdomain.com
- Phone: +1-XXX-XXX-XXXX
```

### External Contacts

```
Law Enforcement (if breach):
- FBI Cyber Division: 1-855-SEE-CYBER
- Local Police Cyber Unit: [Contact info]

Regulatory Agencies (if required):
- Federal Trade Commission: 1-877-IDTHEFT
- State Attorney General: [Contact info]

Professional Services:
- Incident Response Firm: [Contact]
- Forensics Company: [Contact]
```

### Breach Notification Authorities

If data breach confirmed:

```
GDPR (EU):
- Notify within 72 hours
- https://edpb.ec.europa.eu

CCPA (California):
- Notify without unreasonable delay

State Privacy Laws:
- Check individual state requirements
```

---

## Testing the Incident Response Plan

### Quarterly Tabletop Exercise

```
Frequency: Every 3 months
Duration: 2 hours
Participants: Security, IT, Management, Legal

Scenario: [RNG selected from below or custom]
1. Data breach discovered
2. Ransomware attack
3. Denial of service
4. Insider threat
5. System compromise

Exercise:
1. Present scenario
2. Walk through response procedures
3. Discuss decisions and implications
4. Identify gaps
5. Document improvements
```

### Annual Full Simulation

```
Once per year, conduct full test:
1. Prepare test environment
2. Simulate actual incident
3. Execute full response plan
4. Measure response time
5. Test recovery procedures
6. Document results
7. Update procedures based on findings
```

---

## Review & Updates

- **Last Reviewed**: [Date]
- **Next Review**: [Date + 6 months]
- **Last Incident**: [Date and ID]
- **Version**: 1.0

---

**This plan is a living document. Update when:**
- Incident occurs
- Process change
- Personnel change
- Tool/platform change
- Annually minimum

Review and approve by: [Security Manager], [CISO]
