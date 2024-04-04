import subprocess
import roslaunch
import time
import rospy
import os
import json
from std_msgs.msg import String

class Remap:
	
	def __init__(self, time_to_finish = 60):
		"""
		time_to_finish: int : The seconds we'll wait for the robot to map the room
		"""
		self.ttf = time_to_finish
			
	def read_pgm(self, path):
		"""Return a raster of integers from a PGM as a list of lists."""
		lines = open(path, "rb").readlines()
		assert lines[0].strip() == b"P5"
		
		width, height = [int(i) for i in lines[2].split()]
		depth = int(lines[3])
		data = [int(i) for i in lines[4:][0]]
		
		return json.dumps({"width": width, "height": height, "depth": depth, "data": data})
			
	def send_map_to_server(self):
	
		os.system("rosrun map_server map_saver -f /home/ismaeel/maps/map")	
		
		# send the map data to the server
		map_pgm = self.read_pgm("/home/ismaeel/maps/map.pgm")
		
		return map_pgm
	
	def remap(self):
		"""
		When the remap event is called, launch the mapping launch file
		
		returns: true when mapping is done.
		"""

		# the cli args for the launch file
		cli_args = ['/home/ismaeel/catkin_ws/src/BinButler/launch/mapping_launch.launch','']
		
		# setting the launchfile, and args as variables
		roslaunch_args = cli_args[1:]
		roslaunch_file = [(roslaunch.rlutil.resolve_launch_arguments(cli_args)[0], roslaunch_args)]
		
		uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
		
		# launch the file
		
		parent = roslaunch.parent.ROSLaunchParent(uuid, roslaunch_file, verbose=True)
		
		# start the listener, to know when to stop (TODO: DEMO 3)
		#self.listener()
		
		# start the process
		parent.start()
		
		# wait 60 seconds for the mapping to complete (CAN CHANGE TO DYNAMIC IF WE HAVE TIME, probably demo 3)
		time.sleep(self.ttf)
		
		map_pgm = self.send_map_to_server()
		
		# kill the process if it is still running
		parent.shutdown()
		
		# start the naviagtion in the background for path planning

		cli_args = ['/opt/ros/noetic/share/turtlebot3_navigation/launch/turtlebot3_navigation.launch','map_file:=/home/ismaeel/maps/map.yaml', 'open_rviz:=true']
		roslaunch_args = cli_args[1:]
		roslaunch_file = [(roslaunch.rlutil.resolve_launch_arguments(cli_args)[0], roslaunch_args)]
		uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
		parent2 = roslaunch.parent.ROSLaunchParent(uuid, roslaunch_file)

		parent2.start()
		rospy.loginfo("statring nav server...")
		
		return map_pgm
		
	def parsePgm(self, path):
		with open(path, "rb") as file:
		    lines = file.readlines()
		    assert lines[0] == b"P5\n"
		    width, height = [int(i.decode()) for i in lines[2].strip().split()]
		    depth = int(lines[3].decode())
		    data = [int(i) for i in lines[4]]
		    return width, height, depth, data
	


