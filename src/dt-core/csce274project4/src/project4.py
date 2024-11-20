#!/usr/bin/env python3
import rospy
from duckietown_msgs.msg import LanePose, Twist2DStamped

class LaneController:
    def __init__(self):
        """
        Establishes a lane-following node for the duck bot.
        """
        rospy.init_node('lane_following_node')

        # PID parameters for distance (d)
        self.Kp_d = rospy.get_param("~Kp_d", 3.5)
        self.Ki_d = rospy.get_param("~Ki_d", 0.0)
        self.Kd_d = rospy.get_param("~Kd_d", 0.8)

        # PID parameters for angle (phi)
        self.Kp_phi = rospy.get_param("~Kp_phi", 1.0)
        self.Ki_phi = rospy.get_param("~Ki_phi", 0.0)
        self.Kd_phi = rospy.get_param("~Kd_phi", 0.5)

        # Error variables for distance
        self.error_d = 0.0
        self.error_d_prev = 0.0
        self.integral_d = 0.0

        # Error variables for angle
        self.error_phi = 0.0
        self.error_phi_prev = 0.0
        self.integral_phi = 0.0

        # Subscriber for lane pose
        self.sub_lane_pose = rospy.Subscriber(
            "/duck/lane_filter_node/lane_pose",
            LanePose,
            self.control_callback
        )

        # Publisher for velocity commands
        self.pub_cmd_vel = rospy.Publisher(
            "/duck/car_cmd_switch_node/cmd",
            Twist2DStamped,
            queue_size=1
        )

        # Loop rate
        self.rate = rospy.Rate(10)  # 10 Hz
        rospy.loginfo("Lane following node initialized. Duckiebot is attempting to follow the lane.")

    def control_callback(self, msg):
        """
        Callback for processing lane pose data and sending control commands.
        """
        d = msg.d
        phi = msg.phi
        rospy.loginfo(f"Received lane pose: d = {d}, phi = {phi}")

        # Distance PID control
        self.error_d = d
        self.integral_d += self.error_d
        derivative_d = self.error_d - self.error_d_prev
        control_d_error = (
            (self.Kp_d * self.error_d) +
            (self.Ki_d * self.integral_d) +
            (self.Kd_d * derivative_d)
        )

        # Angle PID control
        self.error_phi = phi
        self.integral_phi += self.error_phi
        derivative_phi = self.error_phi - self.error_phi_prev
        control_phi = (
            (self.Kp_phi * self.error_phi) +
            (self.Ki_phi * self.integral_phi) +
            (self.Kd_phi * derivative_phi)
        )

        # Update previous errors
        self.error_d_prev = self.error_d
        self.error_phi_prev = self.error_phi

        # Create and publish the velocity command
        velocity_msg = Twist2DStamped()
        velocity_msg.v = 0.3  # Forward velocity
        velocity_msg.omega = -(control_d_error + control_phi)  # Angular velocity

        self.pub_cmd_vel.publish(velocity_msg)
        rospy.loginfo(f"Published velocity command: v = {velocity_msg.v}, omega = {velocity_msg.omega}")

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    try:
        controller = LaneController()
        controller.run()
    except rospy.ROSInterruptException:
        rospy.loginfo("Lane following node terminated.")


