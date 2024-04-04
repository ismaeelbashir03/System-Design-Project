#!/bin/bash
source /opt/ros/noetic/setup.sh
source ~/catkin_ws/devel/setup.bash
source ~/.bashrc

roslaunch turtlebot3_slam turtlebot3_slam.launch open_rviz:=false
