# python-matter-doorlock
Utility Script for Managing Matter DoorLock Users and Credentials

# Home Assistant

Place the `matter_door_lock.py` in your Home Assistant configuration directory (ensure it is executable)
and add the following to your `configuration.yaml`:

```yaml
shell_command:
  matter_door_lock: ./matter_door_lock.py --nodeId {{node_id}} {{sub_command}}
```

You can then create a script which executes the file (note the Jinja snippet to resolve node ID):

```yaml
sequence:
  - action: shell_command.matter_door_lock
    data:
      node_id: >
        {% set entity_id = 'lock.yale_smart_lock_with_matter' %}
        {% set device_id = device_id(entity_id) %}
        {% set matter_id = device_attr(device_id, 'identifiers') | selectattr(0, 'eq', 'matter') |
           map(attribute=1) | select('match', 'deviceid_.*') | first %}
        {% set node_id = matter_id.split('-')[1] | int(base=16) %}
        {{ node_id }}
      sub_command: >-
        set-user --userIndex {{ user_index }} --userName {{ user_name }}
        --userUniqueID {{ unique_id }} --userType {{user_type}}
    response_variable: response
fields:
  user_index:
    selector:
      text: null
    required: true
    name: User Index
  unique_id:
    selector:
      text: null
    name: Unique Id
    required: true
  user_name:
    selector:
      text: null
    name: User Name
    required: true
  user_type:
    selector:
      text: null
    name: User Type
    required: true
    description: |-
      kUnrestrictedUser
      kYearDayScheduleUser
      kWeekDayScheduleUser
      kProgrammingUser
      kNonAccessUser
      kForcedUser
      kDisposableUser
      kExpiringUser
      kScheduleRestrictedUser
      kRemoteOnlyUser
alias: Set Lock User
description: ""
```
