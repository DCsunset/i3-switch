#! /usr/bin/env python3

import os
import asyncio
import argparse
import signal
import sys
import atexit
from collections import deque
from i3ipc.aio import Connection

pid_file = '{XDG_RUNTIME_DIR}/i3-switch.pid'.format_map(os.environ)
# most recent windows are put at front (initialized after parsing args)
windows = None

async def on_signal(i3, sig):
	root = await i3.get_tree()
	current_container = root.find_focused()
	current_workspace = current_container.workspace().id
	current_window = current_container.id
	scratchpad = root.scratchpad().id

	for window_id in windows:
		# skip current window
		if window_id == current_window:
			continue

		container = root.find_by_id(window_id)
		# ignore window not existing
		if not container:
			continue

		window_workspace = container.workspace().id
		if sig == signal.SIGUSR2 and current_workspace != window_workspace:
			# only switch between windows in the space workspace
			continue
		
		# skip windows in scratchpad
		if window_workspace == scratchpad:
			continue
		
		# switch focus
		cmd = f'[con_id={window_id}] focus'
		await i3.command(cmd)
		break


def exit_handler():
	os.remove(pid_file)


def on_window_focus(conn, event):
	if event.change == 'focus':
		current_window = event.container.id
		# do not insert when the previous window is the same
		if len(windows) > 0 and current_window == windows[0]:
			return

		windows.appendleft(current_window)


async def main():
	with open(pid_file, 'w') as file:
		file.write(str(os.getpid()))
	atexit.register(exit_handler)

	i3 = await Connection(auto_reconnect=True).connect()
	loop = asyncio.get_event_loop()
	loop.add_signal_handler(signal.SIGUSR1, lambda: asyncio.create_task(on_signal(i3, signal.SIGUSR1)))
	loop.add_signal_handler(signal.SIGUSR2, lambda: asyncio.create_task(on_signal(i3, signal.SIGUSR2)))
	i3.on('window::focus', on_window_focus)

	await i3.main()


parser = argparse.ArgumentParser(description="i3 script to switch between windows in history")
parser.add_argument("--max-len", type=int, default=100, help="Max length of the window deque")
args = parser.parse_args()

windows = deque(maxlen=args.max_len)
asyncio.run(main())
