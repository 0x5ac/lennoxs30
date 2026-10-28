# Changelog

All notable changes to this project will be documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

## [2026-10-27]

### Fixed
- manager: config entries created before version 5 failed to load on
  current Home Assistant, which forbids assigning the entry version
  directly during migration.
- manager: a login failure while reconnecting left the connection
  state stuck at Connecting with every entity still available; it now
  reports Login Failed and stops retrying.
- manager: the retry and reconnect loops kept running after the entry
  was unloaded, and unloading while still retrying raised because the
  platforms had never been forwarded.
- manager: enabling "log messages to file" opened the log on the event
  loop during setup, which Home Assistant reports as a blocking call
  (#412).
- manager: on cloud connections the controller was never recorded as
  equipment 0, so the alert sensors warned "Unable to find
  equipment_id [0]" at every start (#432).
- climate: turning a zone off through the climate turn_off service did
  nothing because the handler was never awaited.
- climate: hvac_action exposed raw humidifier states such as
  "humidifying" that are not valid Home Assistant actions.
- config_flow: IPv6 addresses were rejected as invalid hosts.
- number: humidity setpoint entities were created for inactive zones.
- number: the timed ventilation number raised before the first status
  message set the remaining time.
- switch: the ventilation switch raised before the first status
  message set the remaining time.
- switch: turning the parameter safety switch off twice left the first
  rearm timer running, so safety re-engaged early; the timer also
  outlived the entity after a reload.

### Changed
- manager: the unique id rescan after the version 4 migration runs
  once per connection instead of on every reconnect.
