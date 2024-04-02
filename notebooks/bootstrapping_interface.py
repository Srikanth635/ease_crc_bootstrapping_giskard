#!/usr/bin/env python3
import json
import sys
import os

from rosprolog_client import Prolog, atom
from utils.utils import Datapoint, Pose
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Optional
import time

from tqdm import tqdm
class BootstrapInterface:
    """
        Low-level interface to KnowRob, which enables the easy creation of NEEMs in Python.
        It provides bootstrapping predicates that can be used to create a task learning experience between teacher and a robot student
        """

    def __init__(self):
        self.prolog = Prolog()

    """
    * task_request: here the task request can be natural language sentence, we will parse this sentece and create a skill definition from it.
    * this method will have an interface will mongo skill collection which it will query to get the skill and plan from it.
    """
    def request(self, task_reqest: str):
        # TODO: Send the task request to RASA and get back the action core representation, and take action_verb and substance out and create a skill definition.
        # e.g. request("Pour coffee from pitcher to the cup")
        # TODO: now. Check if the mongo skill collection already has this task?

        skill = "pour_coffee"
        # if mongo collection does not have this skill then the response of this method will be.
        # if(skill not found)
        response = "Sorry, I do not know how to " + skill + ". Can you teach me how to do that?"
        # if the mongo collection has found the skill, the response can be.
        skill_plan_count = 1 # ask mongodb and see how many plans do we have for requested task
        task_plan = "PickUp: source_obj; Align: source_obj, destination_obj; Tilt: source_obj, PutDown: source_obj"
        response = "Yes, I have found " + skill_plan_count + " plan for " + skill + "\n" + "Here it is: " + task_plan

    def get_type(self, obj):
        response = Prolog().ensure_once(f"""
                        kb_project([
                            findall([Type],(has_type({atom(obj)}, Type)), Type)
                        ]).
                    """)
        return response

