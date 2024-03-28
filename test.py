#!/usr/bin/env python3

import rospy, cv2, cv_bridge, numpy
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist, Vector3
ERROR_CONVERSION = 0.02
FORWARD_CONSTANT = 0.2
class Follower:

        def __init__(self):

                # set up ROS / OpenCV bridge
                self.bridge = cv_bridge.CvBridge()

                # initalize the debugging window
                cv2.namedWindow("window", 1)

                # subscribe to the robot's RGB camera data stream
                self.image_sub = rospy.Subscriber('camera/rgb/image_raw',
                        Image, self.image_callback)
                
                self.robot_movement_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
                self.rate = rospy.Rate(1)  # set to 1 Hz for now

        def image_callback(self, msg):

                # converts the incoming ROS message to OpenCV format and HSV (hue, saturation, value)
                image = self.bridge.imgmsg_to_cv2(msg,desired_encoding='bgr8')
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

                # Note: see class page for hints on this
                lower_yellow = numpy.array([10, 50, 150])
                upper_yellow = numpy.array([20, 255, 255])
                
                # this erases all pixels that aren't yellow
                mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

                # this limits our search scope to only view a slice of the image near the ground
                h, w, d = image.shape
                search_top = int(3*h/4)
                search_bot = int(3*h/4 + 20)
                mask[0:search_top, 0:w] = 0
                mask[search_bot:h, 0:w] = 0

                # using moments() function, the center of the yellow pixels is determined
                M = cv2.moments(mask)
                # if there are any yellow pixels found
                if M['m00'] > 0:
                        # center of the yellow pixels in the image
                        cx = int(M['m10']/M['m00'])
                        cy = int(M['m01']/M['m00'])

                        # a red circle is visualized in the debugging window to indicate
                        # the center point of the yellow pixels
                        # hint: if you don't see a red circle, check your bounds for what is considered 'yellow'
                        cv2.circle(image, (cx, cy), 20, (0,0,255), -1)

                        # TODO: based on the location of the line (approximated
                        #       by the center of the yellow pixels), implement
                        #       proportional control to have the robot follow
                        #       the yellow line

                        image_center = w // 2
                        error = cx - image_center

                        turn_amount = ERROR_CONVERSION * error
                        twist = Twist()
                        twist.linear.x = FORWARD_CONSTANT
                        twist.angular.z = -turn_amount 

                        # Publish the robot's movement command
                        self.robot_movement_pub.publish(twist)
                # twist_msg = Twist(linear=Vector3(0, 0, 0), angular=Vector3(0, 0, 0))
                # self.robot_movement_pub.publish(twist_msg) # Publish 
                # shows the debugging window
                # hint: you might want to disable this once you're able to get a red circle in the debugging window
                cv2.imshow("window", image)
                cv2.waitKey(3)


        def run(self):
                rospy.spin()
                
if __name__ == '__main__':

        rospy.init_node('line_follower')
        follower = Follower()
        follower.run()