import subprocess

class Remap:
	def remap(self):
		
		ls_output=subprocess.Popen(["roslaunch", "explore_lite", "explore.launch"])
		ls_output.communicate()
rm = Remap()
rm.remap()
