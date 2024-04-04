import subprocess
import shlex


def run(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    while True:
        line = process.stdout.readline().rstrip()
        if not line:
            break
        yield line.decode('utf-8')

def run_command(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline().rstrip().decode('utf-8')
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    rc = process.poll()
    return rc

if __name__ == "__main__":
	
	commands = [
		("odom received!", 
		"roslaunch turtlebot3_navigation move_base.launch"),
		
		("jhgjhgjhg", "roslaunch explore_lite explore.launch"),
	]
	
	
	for stopLine, cmd in commands:

		for output in run(cmd):
			print(output)
			if stopLine in output:
				print("--------------------")
				break
