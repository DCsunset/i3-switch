# i3-switch

i3 script to switch between windows in history.

This script is inspired by [i3-swap-focus](https://github.com/olivierlemoal/i3-swap-focus).
It provides a configurable history length and ignore windows in scratchpad.
Besides, it can skip the closed windows or windows not in the current workspace.

## Installation

```
pip install i3-switch
```

## Configuration

Add the following lines to your i3 config file:

```
# Start i3-switch process
exec i3-switch

bindsym $mod+Tab exec pkill -USR1 -F "${XDG_RUNTIME_DIR}/i3-switch.pid"
# Switch in the same workspaces
# bindsym $mod+Tab exec pkill -USR2 -F "${XDG_RUNTIME_DIR}/i3-switch.pid"
```

To change the max length of the window history records in your i3 config:

```
exec i3-switch --max-len 1000
```
