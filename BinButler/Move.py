import rospy
from geometry_msgs.msg import Twist
import time

class Move:

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
			 
		
			
		
	def shutdown(self):
		# You can stop turtlebot by publishing an empty Twist message 
		rospy.loginfo("Stopping TurtleBot")
		# 
		self.cmd_vel.publish(Twist())
		# Give TurtleBot time to stop
		rospy.sleep(1)
		


