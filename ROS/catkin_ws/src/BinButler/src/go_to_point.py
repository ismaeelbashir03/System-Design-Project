#!/usr/bin/env python
import rospy
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, Point, Quaternion, PoseWithCovarianceStamped
from sensor_msgs.msg import LaserScan
import tf
import roslaunch
import time

class GoToPose():
	"""
	Class for going to a specific point on a map
	"""

	def __init__(self):
	
		rospy.init_node("move_to_point", anonymous=True)
    	
		self.goal_sent = False

		# What to do if shut down (e.g. Ctrl-C or failure)
		rospy.on_shutdown(self.shutdown)
		
		# Tell the action client that we want to spin a thread by default
		self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
		rospy.loginfo("Wait for the action server to come up")

		# Allow up to 5 seconds for the action server to come up
		self.move_base.wait_for_server(rospy.Duration(5))
		rospy.loginfo("Done...")
		
		# start the naviagtion in the background for path planning
		cli_args = ['/opt/ros/noetic/share/turtlebot3_navigation/launch/turtlebot3_navigation.launch','map_file:=/app/maps/map.yaml', 'open_rviz:=false']
		roslaunch_args = cli_args[1:]
		roslaunch_file = [(roslaunch.rlutil.resolve_launch_arguments(cli_args)[0], roslaunch_args)]
		uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
		parent2 = roslaunch.parent.ROSLaunchParent(uuid, roslaunch_file)

		parent2.start()
		rospy.loginfo("statring nav server, set 2d pose estimate...")
		time.sleep(30)
		rospy.loginfo("got nav server...")
		# Create a publisher to republish on the /scan topic
		# Make sure to use the same message type as the subscription
		#self.pub = rospy.Publisher('/scan', LaserScan, queue_size=10)

		# Subscribe to the /scan_filtered topic
		#rospy.Subscriber('/scan_filtered', LaserScan, self.callback)
		
	def callback(self, filtered_scan):
		# Here you can process the filtered scan data if needed
		# For now, we'll just republish it as /scan
		self.pub.publish(filtered_scan)
			
		
		
	def listen_to_transform_once(self):
		listener = tf.TransformListener()

		try:
		    # Wait for the transform to be available
		    listener.waitForTransform('/map', '/base_link', rospy.Time(), rospy.Duration(4.0))
		    
		    (trans, rot) = listener.lookupTransform('/map', '/base_link', rospy.Time(0))
		    
		    rospy.loginfo(f"Translation: {trans}")
		    rospy.loginfo(f"Rotation: {rot}")
		    rot = [float(coord) for coord in rot]
		    trans = [float(coord) for coord in trans]
		    return (trans, rot)
		    
		except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException) as e:
		    rospy.logerr("Error while getting transform: %s" % str(e))
		    return ((0,0), (0,0,0,1))
		

	def goto(self, x, y, r1, r2, r3, r4):
		"""
    	Given a position and quaternian, naviagte to the point.
    	
    	pos: dic with "x", "y", "r1"-"r4" keys for position and quaternion (angle) values
    	
    	return: result
    	"""
		#self.goal_sent = True
		
		# init the move base object
		goal = MoveBaseGoal()

		# setup the map and time params
		goal.target_pose.header.frame_id = 'map'
		goal.target_pose.header.stamp = rospy.Time.now()

		# creating the goal from the position and quaternian to the move base pose
		goal.target_pose.pose.position.x = x
		goal.target_pose.pose.position.y = y
		
		goal.target_pose.pose.orientation = Quaternion(r1, r2, r3, r4)
		
		# Start moving the turtlebot to the goal
		self.move_base.send_goal(goal)
		rospy.loginfo("Navigation goal set to x: {}, y: {}, angle: {} {} {} {}".format(x, y, r1, r2, r3, r4))

		# 60 seconds completion time before quiting
		success = self.move_base.wait_for_result(rospy.Duration(300))

		# getting the result after 60 seconds
		state = self.move_base.get_state()
		result = False

		# if we succeeded, return true
		if success and state == GoalStatus.SUCCEEDED:
			rospy.loginfo("goal succeeded")
			result = True

		# otherwise cancel the goal and return false
		else:
			rospy.loginfo("goal failed")
			self.move_base.cancel_goal()


		self.goal_sent = False
		
		return result

	def shutdown(self):
		"""
		On ros shutdown (ctrl + c), cancel the goal and log
		"""
		if self.goal_sent:
			self.move_base.cancel_goal()
			
		rospy.loginfo("Stop")
		rospy.sleep(1)
	
	def move(self, direction, speed = 1, turn_speed = 1, duration = 1, turn_duration = 0.5):

		rospy.init_node('Basic_controls', anonymous=False)
		self.cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size=10)
		rospy.on_shutdown(self.shutdown)
		
		rate = rospy.Rate(10);
		
		move_cmd = Twist()
		
		if direction == "forward":
			move_cmd.linear.x = speed
		elif direction == "back":
			move_cmd.linear.x = -speed
		elif direction == "left":
			move_cmd.linear.x = 0
		elif direction == "right":
			move_cmd.linear.x = 0	
		
		if direction == "forward":
			move_cmd.angular.z = 0
		elif direction == "back":
			move_cmd.angular.z = 0
		elif direction == "right":
			move_cmd.angular.z = -turn_speed
		elif direction == "left":
			move_cmd.angular.z = turn_speed
		
		if direction == "forward":
			t_end = time.time() + duration
			while time.time() < t_end:
			
			    # publish the Twist values to the TurtleBot node /cmd_vel_mux
			    self.cmd_vel.publish(move_cmd)
			    # wait for 0.1 seconds (10 HZ) and publish again
			    rate.sleep()
		    
		elif direction == "back":
			t_end = time.time() + duration
			while time.time() < t_end:
			
			    # publish the Twist values to the TurtleBot node /cmd_vel_mux
			    self.cmd_vel.publish(move_cmd)
			    # wait for 0.1 seconds (10 HZ) and publish again
			    rate.sleep()
			
		elif direction == "left":
			t_end = time.time() + turn_duration
			while time.time() < t_end:
			
			    # publish the Twist values to the TurtleBot node /cmd_vel_mux
			    self.cmd_vel.publish(move_cmd)
			    # wait for 0.1 seconds (10 HZ) and publish again
			    rate.sleep()
			
		elif direction == "right":
			t_end = time.time() + turn_duration
			while time.time() < t_end:
			
			    # publish the Twist values to the TurtleBot node /cmd_vel_mux
			    self.cmd_vel.publish(move_cmd)
			    # wait for 0.1 seconds (10 HZ) and publish again
			    rate.sleep()

