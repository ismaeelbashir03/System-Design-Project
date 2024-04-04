import subprocess
from io import StringIO

def run(command, stop=None, kill=False):
	print('=== RUNNING ===', command)

	buf = StringIO()
	process = subprocess.Popen(command, stdout=buf, shell=True)

	if stop == None:
		print('=== STOPPING ===', command)	
		

	while True:
		line = buf.getvalue()
		if not line: break
		print(line)
		if stop in line:
			print('=== STOPPING ===', command)	
			if kill:
				process.terminate()
				break
			else:
				break

slam = ('roslaunch turtlebot3_slam turtlebot3_slam.launch open_rviz:=true', None, False)
sleep = ('sleep 5', None, True)
movement = ('roslaunch turtlebot3_navigation move_base.launch', 'odom received', False)
frontier = ('roslaunch explore_lite explore.launch', '', True)

commands = [slam, sleep, movement, frontier]

for command, stop, kill in commands:
    run(command, stop, kill)
