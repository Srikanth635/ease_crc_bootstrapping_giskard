#!/bin/bash
source ${ROS_WS}/devel/setup.bash

roscore &
roslaunch --wait rvizweb rvizweb.launch &
#roslaunch --wait rvizweb rvizweb.launch config_file:=/home/${NB_USER}/bootstrapping_giskard/binder/rvizweb_config.json &

MUJOCO_WORLD_PATH=${ROS_WS}/src/mujoco_world/mujoco_world
mkdir ${MUJOCO_WORLD_PATH}/mujoco_world
ln -s ${MUJOCO_WORLD_PATH}/model ${MUJOCO_WORLD_PATH}/mujoco_world/model

# Start MongoDB and save data on working directory
MONGODB_URL=mongodb://127.0.0.1:27017
mkdir -p ${PWD}/mongodb/data
mongod --fork --logpath ${PWD}/mongodb/mongod.log --dbpath ${PWD}/mongodb/data

# Launch Knowrob
#source ${KNOWROB_WS}/devel/setup.bash
#export KNOWROB_MONGODB_URI=${MONGODB_URL}/?appname=knowrob
#roslaunch --wait knowrob knowrob.launch &



exec "$@"
