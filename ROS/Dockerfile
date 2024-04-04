FROM ros:noetic

WORKDIR /app

# Install ROS packages
RUN apt-get update && apt-get install -y
RUN apt-get install -y ros-noetic-turtlebot3
RUN apt-get install -y ros-noetic-rviz
RUN apt-get install -y ros-noetic-dwa-local-planner
RUN apt-get install -y pip
RUN pip install websockets
RUN apt-get install -y nano

# Copy files
COPY launch /app/launch
COPY maps  /app/maps
COPY catkin_ws /app
COPY scripts /app/scripts

# compile the src code
#RUN chmod +x /app/scripts/setup.sh
#RUN /opt/ros/noetic/setup.sh
#RUN catktin_make

# make the script executable
RUN ["chmod", "+x", "/app/scripts/setup.sh"]

# Set environment variables
ENV TURTLEBOT3_MODEL=waffle

# Run navigation launch file
CMD ["/app/scripts/setup.sh"]
