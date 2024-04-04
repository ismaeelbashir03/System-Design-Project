from grove.adc import ADC
import time
import numpy as np

class Sensor:
	"""
	Info:
		Under 4 < 100
		Under 7 < 75
		Under 12  < 50%
		Under 20 < 25%
		Under 25  = 12.5%
		Over = 0%
	"""

	adc = ADC()
	port_1 = 1
	port_2 = 3

	def measure_distance(self, port):
		"""
		Measuring the distance between the sensor and the reading.

		Args:
			port of the rPi that has the sensor
		"""
		reading = Sensor.adc.read(port)
		distance = 2076/(reading - 11)
		return distance

	def run(self, port):
		"""
		Gets readings from the sensor and smoothes them.

		Args:
			port of the rPi that has the sensor. 
		"""


		# getting the distances of the readings
		distances = []
		for i in range(0,5):
			distance = self.measure_distance(port)
			distances.append(distance)
		
		# sorting and filtering the readings
		distances.sort()
		filtered_arr = []
		for i in range(len(distances)):
			distance_lower = float('inf')
			distance_upper = float('inf')
			
			# only positive readings 
			if i > 0:
				distance_lower = abs(distances[i] - distances[i-1])
			# setting an upper bound
			if i < len(distances) - 1:
				distance_upper = abs(distances[i] - distances[i+1])
			
			# getting the smoothed value
			total = min(distance_upper, distance_lower)
			if total <= 3:
				filtered_arr.append(distances[i])

		if filtered_arr == []:
			return 'NA'
		
		# returning the median
		return np.median(filtered_arr)

	def percentage_conversion(self, reading, sensor):
		"""
		Converts the reading to a percentage.

		it works.
		"""
		if sensor == 1:
			if reading == 'NA':
				percent = -1
			elif reading >= 17:
				percent = 33
			elif reading >= 15:
				percent = 0
			elif reading >= 10:
				percent = 33
			elif reading >= 5:
				percent = 66
			else:
				percent = 100
			return percent
		else:
			if reading == "NA":
				percent = -1
			elif reading >= 19:
				percent = 33
			elif reading >= 17:
				percent = 0
			elif reading >= 10:
				percent = 33
			elif reading  >= 5:
				percent = 66
			else:
				percent = 100
			return percent

	def mode(self, arr):
		"""
		Calculating the mode of the values and the frequency
		"""
		frequency = {}
		
		# get the frequency
		for num in arr:
			frequency[num] = frequency.get(num, 0) + 1
		max_frequency = max(frequency.values())
		
		# returning the frequency
		for key, value in frequency.items():
			if value == max_frequency:
				return key
			
	def sense_once(self):
		"""
		Function for our worker thread to continously read the sensors.
		"""
		percentages_1 = []
		percentages_2 = []

		# getting the readings 5 times
		for _ in range(0,5):
			percentages_1 = []
			percentages_2 = []
			reading_1 = self.percentage_conversion(self.run(Sensor.port_1), 1)
			reading_2 = self.percentage_conversion(self.run(Sensor.port_2), 2)
			percentages_1.append(reading_1)
			percentages_2.append(reading_2)

		# getting the mode of these readings for each sensor and returning them
		mode_1 = self.mode(percentages_1)
		mode_2 = self.mode(percentages_2)

		return mode_1, mode_2