# python-matter-doorlock

A Utility Script for Managing Matter DoorLock Users and Credentials

This script communicates via the [python-matter-server](https://github.com/matter-js/python-matter-server) websocket.

# Standalone Installation

Create a virtual environment and install the package.

```sh
python -m venv .venv
source .venv/bin/activate
pip install .
```

# Usage

```console
% ./matter_door_lock.py -h          
usage: matter_door_lock.py [-h] --nodeId NODEID [--websocketUrl WEBSOCKETURL] [--timeout TIMEOUT]
                           {set-user,get-user,clear-user,set-credential,get-credential,clear-credential} ...

Matter Door Lock Utility

positional arguments:
  {set-user,get-user,clear-user,set-credential,get-credential,clear-credential}

options:
  -h, --help            show this help message and exit
  --nodeId NODEID
  --websocketUrl WEBSOCKETURL
  --timeout TIMEOUT
```

### Example

To create your first user and pin:

```sh
./matter_door_lock.py --nodeId 3 --set-user --userIndex 1 --userName Test --userUniqueID 1234 \
  --userType kUnrestrictedUser
./matter_door_lock.py --nodeId 3 --set-credential --userIndex 1 --credentialIndex 1 --pin 6789
```

# Home Assistant

Requires the [Matter integration](https://www.home-assistant.io/integrations/matter/) to be installed. This will ensure
that the appropriate Python dependencies are available instead of having to create a separate environment.

Place the `matter_door_lock.py` in your Home Assistant configuration directory (ensure it is executable) and add the
following to your `configuration.yaml`:

```yaml
shell_command:
  matter_door_lock: ./matter_door_lock.py --nodeId {{node_id}} {{sub_command}}
```

You can then create a script which executes the file (note the Jinja snippet to resolve node ID):

```yaml
sequence:
  - action: shell_command.matter_door_lock
    data:
      node_id: >-
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
