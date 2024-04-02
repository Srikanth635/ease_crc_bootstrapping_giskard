#!/bin/bash

#source activate rasa38

MONGODB_URL=mongodb://127.0.0.1:27017
mkdir -p ${PWD}/mongodb/data
mongod --fork --logpath ${PWD}/mongodb/mongod.log --dbpath ${PWD}/mongodb/data

export KNOWROB_MONGODB_URI=${MONGODB_URL}/?appname=knowrob

roslaunch --wait knowrob knowrob.launch &
