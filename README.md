# Apply command
A plugin for rhythbox to open playing song in external program (for example nemo or nautilus).

![Example](https://github.com/Janych/apply_command/raw/master/screenshots/aplly_command.png)

## Requirements:
- Rhythmbox 3 or above

## Installation:
- Download the project.
- Extract the files
- Run:
```
./install.sh
```
- Open rhythmbox, go to Tools > Plugins > Apply Command to activate it.
- There You can change "Open" command in Preferences (in parameters accepted %F, %U, %f and %u macros)

## Remove:
```
./install.sh --uninstall
```

Instead of downloading you can just clone the project to your plugin path:
```
$ mkdir -p ~/.local/share/rhythmbox/plugins/apply_command
$ cd ~/.local/share/rhythmbox/plugins/apply_command
$ git clone https://github.com/Janych/apply_command.git
```
For updating:
```
$ cd ~/.local/share/rhythmbox/plugins/apply_command
$ git pull
```

