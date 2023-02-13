# OBS Web Socket Commands
A list of commands that can be sent to OBS via the Web Socket plugin. This project contains only a subset of all
available commands, and is mostly focused on the commands that are useful for recording. The main point of the 
implemented commands is to be chainable, i.e.: the control only returns once a command is executed and the OBS 
reports the new state. Or in more practical terms: the `switch-profile-and-scene-collection` command is the only
reason for this package to exist.

# Usage

You can execute a single command from the command line:
```shell
obws-command pause-record
```
This assumes the `config.toml` file is in the current directory.

---

Or you can call a command from inside a script:
```python
from obwsc.commands.pause_record import PauseRecord

config = {'host': 'localhost', 'port': 4455, 'password': 'secret'}
PauseRecord(config).execute()
```