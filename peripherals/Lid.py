from motors import Motors
from time import time, sleep
from grove.gpio import GPIO

class Lid():
	
	def __init__(self, motor_id_left = 0, left_button_close = 12, left_button_open = 5, motor_id_right = 0, right_button_close = 12, right_button_open = 5, speed = 77, close_buff = 3):
		"""
		
		"""
		# parameters
		self.motor_id_left = motor_id_left
		self.motor_id_right = motor_id_right
		self.speed = speed
		self.close_buff = close_buff

		# motor class
		self.mc = Motors()

		# the button pins
		self.left_close_button = GPIO(left_button_close, GPIO.IN)
		self.left_open_button = GPIO(left_button_open, GPIO.IN)
		self.right_close_button = GPIO(right_button_close, GPIO.IN)
		self.right_open_button = GPIO(right_button_open, GPIO.IN)

		# the state
		self.state = {"left": "closed", "right": "closed"}

	def stop(self):
		"""
		USED FOR DEBUGGING, STOPS ALL MOTOR FUNCTIONS
		"""
		self.mc.stop_motors()

	def open(self, side="left"):
		"""
		open the lid
		"""
		# if we are already open, dont open again
		if self.state[side] == "opened": 
			print("already opened!")
			return

		if side == "left":
			motor_id = self.motor_id_left
			open_button = self.left_open_button
		if side == "right":
			motor_id = self.motor_id_right
			open_button = self.right_open_button

		# starting the motor
		self.mc.move_motor(motor_id, self.speed)

		self.state[side] = "opened"

		# while the button is not pressed continue moving
		while True:
			if open_button.read():
				print("pressed open, stopping motor...")
				break

			sleep(0.001)

		# keep motor up
		self.mc.move_motor(motor_id, 35)



	def close(self, side = "left"):
		"""
		close the lid
		"""

		# if we are already closed, dont close again
		if self.state == "closed": 
			print("already closed!")
			return

		if side == "left":
			motor_id = self.motor_id_left
			close_button = self.left_close_button
		if side == "right":
			motor_id = self.motor_id_right
			close_button = self.right_close_button

		# starting the motor
		self.mc.move_motor(motor_id, -self.speed // self.close_buff)

		self.state[side] = "closed"

		# while the button is not pressed continue moving
		while True:
			# if we have hit the button stop closing
			if close_button.read():
				print("pressed close, stopping motor...")
				self.mc.stop_motor(motor_id)
				return

			sleep(0.001)

# testing
if __name__ == "__main__":

	l = Lid(motor_id_left = 2, left_button_close = 18, left_button_open = 5, motor_id_right = 0, right_button_close = 24, right_button_open = 22, speed = 87, close_buff = 3)

	while True:
		choice = input("open recycling/general/both lids: ")
		if choice == "recycling":
			l.open("left")
			print("opened")
			sleep(2)
			print("closed")
			l.close("left")
		elif choice == "general":
			l.open("right")
			print("opened")
			sleep(2)
			print("closed")
			l.close("right")
		elif choice == "both":
			l.open("right")
			l.open("left")
			sleep(2)
			l.close("right")
			l.close("left")
		elif choice == "q":
			l.mc.stop_motors()
		else:
			print("please choose only 'recycling/general/both/q'.")
