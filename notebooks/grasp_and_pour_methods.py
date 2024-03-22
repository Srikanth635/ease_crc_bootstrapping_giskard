#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped, Vector3Stamped, PointStamped, Quaternion, Point
from tf.transformations import quaternion_about_axis, quaternion_from_matrix

from giskardpy.python_interface.python_interface import GiskardWrapper
from giskardpy.utils.tfwrapper import lookup_pose


def openGripper(giskard: GiskardWrapper):
    giskard.motion_goals.add_motion_goal(motion_goal_class='CloseGripper',
                                         name='openGripper',
                                         as_open=True,
                                         velocity_threshold=100,
                                         effort_threshold=1,
                                         effort=100)
    giskard.motion_goals.allow_all_collisions()
    giskard.add_default_end_motion_conditions()
    giskard.execute()


def closeGripper(giskard: GiskardWrapper):
    giskard.motion_goals.add_motion_goal(motion_goal_class='CloseGripper',
                                         name='closeGripper')
    giskard.motion_goals.allow_all_collisions()
    giskard.add_default_end_motion_conditions()
    giskard.execute()


def align_to(giskard: GiskardWrapper, side: str, axis_align_to_z: Vector3Stamped, object_frame: str, control_frame: str,
             axis_align_to_x: Vector3Stamped = None, distance=0.3, height_offset=0.0, second_distance=0.0):
    """
    side: [front, left, right] relative to the object frame from the pov of a robot standing at the origin of the world frame
    axis_align_to_z: axis of the control_frame that will be aligned to the z-axis of the object frame
    object_frame: name of the tf frame to align to
    control_frame: name of a tf frame attached to the robot that should be moved around
    axis_align_to_x: axis of the control_frame that will be aligned to the x-axis of the object frame
    distance: distance between the object and the control frame along the axis resulting from align to [side]
    height_offset: offset between the two frames on the z-axis
    second_distance: offset on the last free axis. When side == [left, right] this is the x axis of the object frame, otherwise it is the y axis.
    """
    goal_normal = Vector3Stamped()
    goal_normal.header.frame_id = object_frame
    goal_normal.vector.z = 1
    giskard.motion_goals.add_align_planes(goal_normal, control_frame, axis_align_to_z, 'map', name='align_upright')
    if axis_align_to_x:
        second_goal_normal = Vector3Stamped()
        second_goal_normal.header.frame_id = object_frame
        second_goal_normal.vector.x = 1
        giskard.motion_goals.add_align_planes(second_goal_normal, control_frame, axis_align_to_x, 'map',
                                              name='align_second')

    goal_position = PointStamped()
    goal_position.header.frame_id = object_frame
    if side == 'front':
        goal_position.point.x = -distance
        goal_position.point.y = second_distance
        goal_position.point.z = height_offset
    elif side == 'left':
        goal_position.point.x = second_distance
        goal_position.point.y = distance
        goal_position.point.z = height_offset
    elif side == 'right':
        goal_position.point.x = second_distance
        goal_position.point.y = -distance
        goal_position.point.z = height_offset
    giskard.motion_goals.add_cartesian_position(goal_position, control_frame, 'map')
    giskard.add_default_end_motion_conditions()
    giskard.execute()


def tilt(giskard: GiskardWrapper, angle: float, velocity: float, rotation_axis: Vector3Stamped, controlled_frame: str):
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = controlled_frame
    goal_pose.pose.orientation = Quaternion(
        *quaternion_about_axis(angle, [rotation_axis.vector.x, rotation_axis.vector.y, rotation_axis.vector.z]))
    giskard.motion_goals.add_cartesian_pose(goal_pose, controlled_frame, 'map')
    giskard.motion_goals.add_limit_cartesian_velocity(tip_link=controlled_frame, root_link='map',
                                                      max_angular_velocity=velocity)
    giskard.add_default_end_motion_conditions()
    giskard.execute()

def move_arm(giskard: GiskardWrapper, direction: str, control_frame: str):
    goal_pose = lookup_pose('map', control_frame)
    if direction == 'up':
        goal_pose.pose.position.z += 0.1
    elif direction == 'down':
        goal_pose.pose.position.z -= 0.1
    elif direction == 'left':
        goal_pose.pose.position.y += 0.1
    elif direction == 'right':
        goal_pose.pose.position.y -= 0.1
    elif direction == 'forward':
        goal_pose.pose.position.x += 0.1
    elif direction == 'back':
        goal_pose.pose.position.x -= 0.1

    giskard.motion_goals.add_cartesian_pose(goal_pose=goal_pose, tip_link=control_frame, root_link='map')
    giskard.add_default_end_motion_conditions()
    giskard.execute()

# def put_down(giskard: GiskardWrapper, location: PoseStamped, control_frame: str):
#     giskard.motion_goals.add_cartesian_pose(goal_pose=location, tip_link=control_frame, root_link='map')
#     giskard.add_default_end_motion_conditions()
#     giskard.execute()

def grasp(giskard: GiskardWrapper, object_name: str, robot_eeff: str, grasp_side: str, upright_axis: str, second_axis: str):
    # Here starts the control
    # Open the gripper. Needs the giskard interface as input, as all the other methods
    openGripper(giskard)

    # This aligns the control frame to the front of the object frame in a distance of 0.04m.
    align_to(giskard, grasp_side, axis_align_to_z=upright_axis, object_frame=object_name, control_frame=robot_eeff,
             axis_align_to_x=second_axis, distance=0.04)

    # Close the gripper
    closeGripper(giskard)
    giskard.execute()

def pick_up(giskard:  GiskardWrapper, object_name: str, robot_eeff: str, grasp_side: str, upright_axis: str, second_axis: str):

    # first make an roslaunch giskardpy giskardpy_hsr_mujoco.launchattempt at grasping an object
    grasp(giskard, object_name, robot_eeff, grasp_side, upright_axis, second_axis)

    # # now, move the arm upward
    move_arm(giskard, 'up', robot_eeff)


def put_down(giskard: GiskardWrapper, goal_pose: PoseStamped, control_frame: str):

    goal_pose = lookup_pose('map', control_frame)
    giskard.motion_goals.add_cartesian_pose(goal_pose=goal_pose, tip_link=control_frame, root_link='map')
    giskard.add_default_end_motion_conditions()
    giskard.execute()
    # giskard.add_default_end_motion_conditions()
    # open the gripper
    openGripper(giskard)
    giskard.execute()
    # # now, move the arm upward
    # move_arm(giskard, 'up', robot_eeff)
