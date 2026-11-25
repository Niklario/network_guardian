# Network Guardian — Master Development Prompt

## 1. Project introduction

Network Guardian is a self-hosted, privacy-focused network monitoring, security analysis and eventually active network defence platform, developed as a custom Home Assistant app (add-on).

The long-term ambition is to create an intelligent network watchdog that continuously monitors a private network, learns the normal behaviour of individual devices, identifies suspicious activity, notifies the administrator and eventually takes controlled defensive actions.

The application should evolve into a comprehensive local network security centre, inspired by professional platforms such as UniFi Network, enterprise network monitoring systems and Network Detection and Response (NDR) solutions.

Network Guardian should be an independent security platform, not simply an alternative frontend for AdGuard Home.

AdGuard Home is currently its primary data source.

## 2. Core principles

The following principles must be respected throughout development:

- Local-first architecture.
- Privacy by design.
- No cloud-based processing.
- No external AI services.
- No telemetry.
- No external JavaScript, CSS libraries or CDN dependencies.
- No unnecessary external connections.
- Minimal resource consumption.
- Modular and maintainable source code.
- Persistent local storage.
- Security-conscious architecture.
- Responsive, professional user interface.
- Transparency in security decisions.
- User control over automated defensive actions.

The application should eventually operate without internet access while allowing ordinary network devices to continue accessing the internet normally.

Local processing alone must not be confused with enforced network isolation.

AI is not required for the initial versions. Statistical analysis and deterministic security rules should be prioritised. An optional local AI engine may be introduced later if it provides measurable benefits.

## 3. Current environment

### Hardware

- Raspberry Pi 5
- 8 GB RAM
- 500 GB M.2 SSD
- Home Assistant OS

### Existing infrastructure

- Home Assistant
- AdGuard Home running as a Home Assistant app
- TP-Link Archer AX73 router
- Managed and unmanaged network switches
- Synology NAS
- Plex Media Server
- IoT devices
- Smart TVs
- Mobile phones
- Computers

### Future infrastructure

The network may eventually migrate to a Ubiquiti UniFi infrastructure, including:

- UniFi Cloud Gateway
- Managed UniFi switches
- UniFi wireless access points
- Multiple VLANs
- Network segmentation
- RADIUS authentication
- Network Access Control
- Device registration and quarantine networks

Network Guardian must remain compatible with the existing infrastructure and should not require UniFi hardware to function.

Future network integrations should use modular adapters.

## 4. Current project status

Current version: **v0.3.0**

Network Guardian is installed and running successfully as a local Home Assistant app.

The dashboard is accessible through Home Assistant Ingress and the Home Assistant sidebar.

The application has successfully collected real DNS traffic, stored it in SQLite and displayed the collected information through its web interface.

At the time of the latest dashboard verification:

- 2,250 recorded DNS requests.
- 16 observed client IP addresses.
- 898 blocked DNS requests.
- 39.9% blocking rate.

These figures represent the current collected dataset, not hardcoded application values or necessarily a complete 24-hour observation period.

## 5. Existing architecture

Project location:

`/addons/network_guardian/`

Current file structure:

```text
network_guardian/
├── config.yaml
├── Dockerfile
├── main.py
├── adguard.py
├── database.py
├── collector.py
├── devices.py
├── analyzer.py
├── notifier.py
├── dashboard.py
└── dashboard.html
```

### Technology stack

- Python 3.12
- Python standard library
- SQLite
- HTML
- CSS
- Vanilla JavaScript
- Docker
- Home Assistant Ingress

The application currently uses a lightweight architecture without additional Python dependencies.

Do not introduce large frameworks or unnecessary dependencies without explaining their benefits and resource requirements.

## 6. AdGuard Home integration

Network Guardian communicates directly with AdGuard Home using its local HTTP API.

API address:

`http://127.0.0.1:45158`

Current verified AdGuard Home version:

`v0.107.80`

The application uses host networking to access the local API.

The following endpoints have been successfully tested:

```text
GET /control/status
GET /control/querylog
```

A client endpoint is implemented in the API adapter but has not yet been independently verified:

```text
GET /control/clients
```

The status and query log endpoints currently work without additional authentication in this installation.

Do not assume that this will be true for every installation.

The API provides information including:

- Client IP address
- Client information
- Requested domain
- DNS record type
- Timestamp
- DNS response status
- Returned IP addresses
- Blocking reason
- Applied filtering rules
- Response time
- Cache status
- Upstream DNS server

The integration must remain read-only until active defensive functionality has been deliberately implemented and tested.

## 7. Existing DNS collection engine

The DNS collection engine is operational.

Current functionality includes:

- Polling AdGuard Home every 10 seconds.
- Configurable polling interval.
- Fetching DNS requests in batches of 500.
- Pagination through older DNS requests.
- Persistent collection checkpoints.
- A 60-second overlapping collection window.
- SHA-256-based event identification.
- SQLite duplicate prevention.
- Automatic reconnection following API errors.
- Initial import of approximately one hour of historical DNS activity.
- Automatic retention cleanup.

Pagination and duplicate prevention have been demonstrated during normal operation.

Collection completeness under high traffic, extended downtime and API log rotation still requires testing.

The collector must eventually detect and report potential gaps in collected data.

## 8. Database

Database location:

`/data/network_guardian.db`

The database is stored in the persistent Home Assistant app data directory.

Current tables:

- `dns_queries`
- `security_events`
- `metadata`

The database uses SQLite WAL mode and indexed queries.

Current DNS retention period:

30 days.

Future database development should include:

- Persistent device identities.
- Device aliases.
- MAC addresses.
- Historical IP assignments.
- Device classifications.
- Domain classifications.
- Behavioural baselines.
- Security incidents.
- Administrator decisions.
- Approved domains.
- Blocked domains.
- Device trust levels.
- Configuration history.
- Audit logs.
- Database schema migrations.
- Historical aggregated statistics.

Existing databases must be preserved during application updates.

Never require deletion of the existing database as a normal upgrade procedure.

## 9. Existing device monitoring

Network Guardian currently creates device profiles based on observed client IP addresses.

Current statistics include:

- Total DNS requests.
- Unique requested domains.
- Blocked requests.
- First observed activity.
- Last observed activity.
- Recently active clients.

The current implementation does not reliably identify physical devices.

An IP address must not be treated as a permanent device identity because of DHCP, IP reassignment, randomised MAC addresses and network changes.

Future device identification should combine available information from:

- MAC addresses.
- DHCP leases.
- Hostnames.
- AdGuard client information.
- ARP and neighbour tables.
- Home Assistant device trackers.
- Router integrations.
- UniFi integrations.
- Manually assigned device names.

Network Guardian should distinguish between confirmed identities and inferred identities.

## 10. Existing behaviour analysis

Network Guardian currently contains a basic statistical anomaly detection engine.

The default learning period is seven days.

The implemented detection categories are:

### DNS Traffic Spike

Detects unusually high DNS request volumes compared with historical hourly activity.

### New Domain Burst

Detects a large number of previously unseen domains requested by a device within an hour.

### High Block Rate

Detects unusually high proportions of blocked DNS requests.

### NXDOMAIN Burst

Detects repeated requests for domains that do not exist.

The current implementation analyses completed hourly periods and uses preliminary statistical thresholds.

Security events are stored locally and printed in the application log.

Repeated events of the same type for the same client are subject to a cooldown.

The detection engine has not yet completed its initial learning period in the live environment. Its effectiveness and false-positive rate have therefore not been validated.

## 11. Future behaviour analysis

The analysis engine should eventually build an individual behavioural profile for every identified device.

Profiles should consider:

- Normal DNS request frequency.
- Typical active hours.
- Normal domains and services.
- Frequently contacted organisations.
- Normal DNS record types.
- Typical blocking rates.
- Typical response statuses.
- Periodic communication patterns.
- Changes in communication behaviour.
- Newly observed destinations.
- Device-specific activity patterns.

Future detection capabilities may include:

- Potential DNS tunnelling.
- Potential DNS beaconing.
- Domain generation algorithm indicators.
- Excessive DNS failures.
- Unusual subdomain generation.
- Suspicious domain characteristics.
- Sudden changes in device behaviour.
- Previously unseen network destinations.
- Unexpected activity during inactive hours.
- Potentially compromised IoT devices.
- Unexpected tracking and telemetry activity.

Every detection must include supporting evidence.

A new domain, high DNS volume or blocked advertising request must not automatically be classified as malicious.

Security confidence and severity must be evaluated separately.

The analysis engine should learn from administrator feedback and support device-specific exceptions.

## 12. User interface — current priority

The existing dashboard is functional but visually immature.

The immediate development priority is a complete UI and UX redesign.

The interface should feel like a professional network security product rather than a basic Home Assistant dashboard or a collection of HTML cards.

### Current UI problems

- Excessive padding and unused space.
- Oversized navigation buttons.
- Navigation wrapping across multiple rows on mobile.
- Large statistics cards with low information density.
- Excessive vertical scrolling.
- Redundant application headings inside Home Assistant.
- Insufficient visual hierarchy.
- Basic charts without useful axis labels.
- Missing chart timestamps and numerical scales.
- Limited visual differentiation between normal, blocked and suspicious activity.
- Insufficient use of available screen space.
- Lack of a consistent design system.
- Limited visibility into monitoring and learning status.

### Design direction

Use a modern, compact, professional dark-mode interface inspired by UniFi Network and enterprise security platforms.

Design characteristics:

- Near-black background.
- Subtle dark surfaces.
- Thin borders.
- Compact typography.
- Consistent spacing.
- Minimal visual noise.
- Clear information hierarchy.
- Restrained use of accent colours.
- Small, meaningful icons.
- Smooth but lightweight interactions.
- Responsive layouts.
- High information density without sacrificing readability.

Avoid:

- Oversized headings.
- Excessively rounded cards.
- Large empty areas.
- Decorative gradients.
- Unnecessary animations.
- Excessive badges.
- Repeated labels.
- Large buttons for ordinary navigation.
- Generic AI-generated dashboard aesthetics.

### Mobile experience

Mobile usability is a primary requirement, not an afterthought.

The application must work naturally inside the Home Assistant Android application.

Use:

- Compact navigation.
- Responsive grids.
- Horizontally scrollable tabs where appropriate.
- Compact metric displays.
- Touch-friendly interactive elements.
- Expandable device details.
- Responsive charts.
- Efficient use of vertical screen space.

Do not simply shrink a desktop layout to fit a mobile screen.

### Desktop experience

The desktop version should take advantage of the available width through:

- Multi-column layouts.
- Compact tables.
- Persistent navigation where appropriate.
- Side panels for contextual information.
- Larger analytical charts.
- Efficient filtering and searching.

## 13. Dashboard sections

### Overview

The main page should immediately communicate the state of the monitoring system and observed network activity.

Include:

- Monitoring status.
- AdGuard API connection status.
- Last successful collection.
- Observed clients.
- DNS request volume.
- Blocked requests.
- Blocking percentage.
- Security events.
- Learning progress.
- DNS activity over time.
- Most active devices.
- Recent security events.
- Recently observed devices.

Support selectable time ranges such as:

- Last hour.
- Last 24 hours.
- Last 7 days.
- Last 30 days.

Clearly distinguish incomplete observation periods from genuine inactivity.

Do not present a network as secure simply because no security events have been detected.

### Devices

Create a comprehensive device management interface.

Each device should eventually display:

- Device name.
- IP address.
- MAC address.
- Manufacturer.
- Device type.
- First seen.
- Last seen.
- Activity status.
- Trust level.
- Learning status.
- DNS request volume.
- Blocking rate.
- Security events.

Selecting a device should open a detailed profile containing its activity timeline, domain history, behavioural baseline and security findings.

Allow manual device naming and classification.

### Live DNS

Provide a real-time DNS activity interface.

Features:

- Automatic refresh.
- Pause and resume.
- Search.
- Client filtering.
- Domain filtering.
- DNS record type filtering.
- Blocking status filtering.
- Response status filtering.
- Expandable DNS event details.
- Efficient pagination or virtualised rendering.

Live updates must not reset the user's scroll position, filters or selected event.

### Domain Explorer

Provide detailed insight into requested domains.

Include:

- Domain name.
- Request count.
- Number of requesting devices.
- First seen.
- Last seen.
- Blocking status.
- DNS record types.
- Returned addresses.
- Domain classification.
- Security observations.

Future functionality should allow administrator-approved domain classification, allowlisting and blocking.

### Security Events

Create a dedicated security investigation interface.

Each event should contain:

- Event type.
- Affected device.
- Timestamp.
- Severity.
- Confidence.
- Supporting evidence.
- Explanation.
- Recommended action.
- Investigation status.

Support acknowledging, dismissing and investigating events.

Security events must be clearly distinguished from ordinary blocked advertising and telemetry requests.

### Learning

Show the progress of behavioural learning for each device.

Include:

- Learning start date.
- Observation duration.
- Available data.
- Baseline readiness.
- Learning progress.
- Data completeness.
- Detected behavioural changes.

A device should not be considered fully learned solely because seven calendar days have passed.

### Settings

Provide a structured settings interface.

Include:

- AdGuard connection settings.
- Polling interval.
- Retention period.
- Learning duration.
- Detection thresholds.
- Notification settings.
- Device identification settings.
- Security policies.
- Application diagnostics.
- Database information.

Sensitive configuration changes must be validated and protected.

## 14. Future security functionality

Network Guardian should eventually support active network defence.

This must be implemented gradually.

### Monitoring mode

Observe and collect information without modifying the network.

This is the current operating mode.

### Detection mode

Identify suspicious behaviour and generate security events.

### Advisory mode

Recommend defensive actions to the administrator.

### Approval mode

Allow the administrator to approve or reject proposed actions.

### Automated defence mode

Automatically perform explicitly authorised, high-confidence defensive actions.

Potential defensive actions include:

- Blocking suspicious domains through AdGuard Home.
- Temporarily blocking domains.
- Applying device-specific DNS policies.
- Alerting the administrator.
- Quarantining devices through supported network infrastructure.
- Restricting device access.
- Moving devices into quarantine VLANs where supported.

Every automated action must support:

- Clear justification.
- Audit logging.
- Administrator visibility.
- Allowlist protection.
- Rollback.
- False-positive handling.
- Expiration where appropriate.

Never overwrite existing AdGuard filtering rules when adding Network Guardian-managed rules.

Automatic blocking must remain disabled by default.

## 15. Future Network Access Control

The long-term objective is to support detection and management of newly connected network devices.

The desired workflow is:

1. An unknown device connects to the network.
2. The device is identified by supported network infrastructure.
3. The device receives restricted or quarantined network access.
4. Network Guardian creates a device registration event.
5. The administrator receives a notification.
6. The administrator approves or rejects the device.
7. Approved devices receive the appropriate network access policy.
8. Rejected devices remain restricted.

Potential technologies include:

- VLANs.
- IEEE 802.1X.
- RADIUS.
- MAC Authentication Bypass.
- Dynamic VLAN assignment.
- UniFi controller integration.
- DHCP monitoring.
- Firewall integration.

Actual capabilities depend on the selected router, switches, access points and authentication infrastructure.

Network Guardian should not assume that DNS monitoring alone can enforce network access control.

## 16. Home Assistant integration

Network Guardian should eventually integrate more deeply with Home Assistant.

Potential entities include:

- Monitoring status.
- Known devices.
- Unknown devices.
- Active security events.
- High-severity events.
- DNS request count.
- Blocked DNS request count.
- Database size.
- Learning progress.
- AdGuard connectivity.
- Collector health.

Future integration should support:

- Mobile push notifications.
- Home Assistant automations.
- Actionable notifications.
- Device approval and rejection.
- Security event acknowledgement.
- Emergency defensive actions.
- Application health monitoring.

The administrator should be able to investigate and respond to events directly from a mobile phone.

## 17. Security requirements

Network Guardian itself must not become a security vulnerability.

Requirements:

- No unnecessary privileged container access.
- No unnecessary exposed ports.
- Administrator-only dashboard access.
- Strict Ingress access controls.
- Parameterised SQL queries.
- Input validation.
- Output escaping.
- Protection against XSS.
- Protection against unauthorised API requests.
- Safe handling of untrusted DNS data.
- Secure handling of credentials.
- Controlled configuration changes.
- Least-privilege access.
- Audit logging.
- Safe failure behaviour.

DNS domains, client names, hostnames and API responses must be treated as untrusted input.

The current use of host networking must be reviewed as the application develops.

The current application does not enforce outbound internet isolation. A future deployment architecture must address this requirement explicitly.

## 18. Performance requirements

The application must remain suitable for continuous operation on a Raspberry Pi 5 alongside Home Assistant and other apps.

Prioritise:

- Low CPU usage.
- Low memory consumption.
- Efficient database queries.
- Appropriate database indexes.
- Incremental statistics.
- Background processing.
- Efficient retention cleanup.
- Minimal frontend dependencies.
- Bounded API responses.
- Efficient chart rendering.

The dashboard must not interfere with DNS collection or security analysis.

Avoid repeatedly scanning the entire DNS history when incremental calculations are possible.

## 19. Development roadmap

### v0.1.0 — API connectivity

Completed:

- Custom Home Assistant app.
- Local AdGuard connection.
- DNS query retrieval.
- Continuous polling.

### v0.2.0 — Collection and analysis engine

Implemented:

- SQLite database.
- Pagination.
- Duplicate prevention.
- Persistent collection checkpoints.
- Client statistics.
- Retention cleanup.
- Initial statistical analysis engine.
- Local security event logging.

Further validation is required for collection completeness and detection accuracy.

### v0.3.0 — Security Dashboard

Implemented and operational:

- Home Assistant Ingress.
- Local web server.
- Overview.
- Devices.
- Live DNS.
- Domain Explorer.
- Security Events.
- Learning.
- Settings.

The dashboard has been successfully opened on a mobile device.

The visual design and usability require substantial improvement.

### v0.4.0 — Professional UI and UX

Immediate development priority:

- Complete dashboard redesign.
- Mobile-first responsive layout.
- Compact navigation.
- Improved charts.
- Consistent design system.
- Better information hierarchy.
- Improved tables and filters.
- Interactive device details.
- Loading, empty and error states.
- Preservation of existing functionality.

### v0.5.0 — Device Intelligence

- Persistent device identities.
- MAC address discovery.
- Hostname discovery.
- Manual device aliases.
- Device classifications.
- Historical IP tracking.
- New device detection.

### v0.6.0 — Behaviour Intelligence

- Improved behavioural baselines.
- Device-specific anomaly detection.
- Data completeness tracking.
- Risk and confidence scoring.
- False-positive management.
- Improved security event explanations.

### v0.7.0 — Notifications and Incident Management

- Home Assistant integration.
- Push notifications.
- Actionable notifications.
- Event acknowledgement.
- Incident investigation.
- Administrator feedback.

### v0.8.0 — Controlled Active Defence

- Domain blocking recommendations.
- Administrator approval.
- Temporary blocking.
- Allowlisting.
- Rollback.
- Security action audit logs.

### v0.9.0 — Network Infrastructure Integration

- Router integrations.
- UniFi integration.
- DHCP monitoring.
- VLAN awareness.
- Network device discovery.
- Supported quarantine mechanisms.

### v1.0.0 — Network Guardian Security Platform

A stable, documented, locally operated network security platform with monitoring, device intelligence, behaviour analysis, incident management and controlled defensive capabilities.

Version assignments beyond the current release are provisional.

## 20. Development instructions

When developing Network Guardian:

1. Inspect the existing source files before making changes.
2. Understand the current architecture and API contracts.
3. Preserve existing functionality.
4. Preserve existing user data.
5. Maintain backward compatibility where practical.
6. Avoid unnecessary rewrites.
7. Keep modules separated by responsibility.
8. Provide complete, working implementations rather than placeholders.
9. Never use hardcoded demonstration data in the production dashboard.
10. Validate syntax and test functionality where possible.
11. Clearly identify untested functionality.
12. Explain architectural changes and security implications.
13. Provide database migrations when necessary.
14. Update application version numbers consistently.
15. Provide clear installation and upgrade instructions.
16. Identify known limitations and outstanding work.
17. Never claim that a feature works unless it has been implemented and appropriately verified.

When making changes, provide complete replacement files or an organised patch with clear file paths.

Do not require the administrator to manually combine numerous disconnected code snippets when complete files can be provided.

## 21. Immediate assignment

Begin development of Network Guardian v0.4.0.

The primary objective is a complete redesign of the existing user interface while preserving the operational backend.

Review the existing dashboard.py and dashboard.html files, the current API endpoints and the supplied screenshot of the running application.

Identify usability, layout, responsiveness and performance problems.

Create a coherent design system and rebuild the frontend into a professional, compact, responsive network security interface.

Prioritise the Overview page and mobile navigation, then apply the same design system consistently across every existing section.

Improve chart readability, data presentation, interaction patterns and system health visibility.

Do not introduce new active defence functionality during this redesign.

Do not compromise the existing DNS collector, database or security architecture.

The finished result should look and behave like a dedicated network security product that could reasonably be distributed to other Home Assistant users, rather than a personal development prototype.
