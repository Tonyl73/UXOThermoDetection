#Based on code from UHDT Software team
#Utilizes MAVROS or ROS to listen in on flight controller, which outputs or publishes drone state(s)

import rospy #TODO NEED TO FIGURE OUT HOW TO IMPORT NECESSARY LIBRARIES
import mavros
import math
#... theres more. See obstacle avoidance repo >> autotest branch >> auto_test3(edited).py

class WaypointMission:
	def __init__(self):
		rospy.init_node('Some_nodename') #initialize as ROS node
		mavros.set_namespace()
		
		#verify state with ROS topics
		self.current_state = State()
		rospy.Subscriber('/mavros/state', State, self.state_callback)
		
		self.pub = rospy.Publisher('/mavros/setpoint_raw/global',GlobalPositionTarget, queue_size=1) #GPS via MAVROS??\
		
		while self.pub.get_num_connections() == 0: #sleep if no connections
			rospy.sleep(.1)
			
	def state_callback(self, msg):
		'''
		ROS callback function to return the state of UAS
		'''
		self.current_state = msg
			
	def is_guided(self):
		'''
		Check if the UAS is in "GUIDED" mode
		Loops until UAS is in "GUIDED" mode
		'''
		
		rospy.loginfo("Waiting to be GUIDED")
		While not (self.current_state.mode == 'GUIDED'):
			rospy.loginfo("Waiting to be GUIDED")
			rospy.sleep(1)
		rospy.loginfo("Now in GUIDED mode")
		
	
if __name__ = '__main__':
	
	#intialize the mission object of some sort
	#mission = WaypointMission()
	#set parameters
	#mission.set_param('WPNAV_SPEED',2000) cm/s
	#mission.set_param('WPNAV_configthing',value) cm/s
	#mission.set_param('WPNAV_configthing',value) cm/s
	#mission.set_param('WPNAV_configthing',value) cm/s
	#mission.is_guided()
	#Ideally once the loop within mission.is_guided() resolves it self (guided mode detected), anything we put after this will run.
	
	
	
	
