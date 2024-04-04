#!/usr/bin/env python3
import sys
import os
sys.path.append(os.getcwd() + "/../")
from binder.rasa.scripts.intents import Intent
from binder.rasa.scripts.parse_instruction_rasa import query_rasa
from rosprolog_client import Prolog, atom
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
# Create or access the database
db = client['bootstrapping']

# Create or access the collection
collection = db['skills']


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
        result = query_rasa(task_reqest)
        print("rasa results: ", result)
        # e.g. request("Pour coffee from pitcher to the cup")
        skill_name = ""
        if result['intent'] == Intent.POURING.value:
            skill_name = result['intent'] + " " + result['substance']
            field_name = 'skill_name'
            field_value = skill_name
        elif result['intent'] == Intent.CUTTING.value:
            skill_name = result['intent'] + " " + result['cuttie']
            field_name = 'skill_name'
            field_value = skill_name

        # Query documents for the specified field
        cursor = collection.find({field_name: field_value})
        # Check if the mongo skill collection already has this task?
        # Iterate over the query results
        skill_found = False
        for document in cursor:
            if document:
                skill_found = True
                response = "Yes, I have found " + skill_name + "\n"
                print(response)

        if not skill_found:
            # TODO: do this when the bootstrapping session is finished
            # add_skill_to_db(skill_name)
            response = "Sorry, I do not know how to " + skill_name + ". Can you show me how to do this?"
            print(response)

        # skill = "pour_coffee"
        # if mongo collection does not have this skill then the response of this method will be.
        # if(skill not found)

        # if the mongo collection has found the skill, the response can be.
        # skill_plan_count = 1  # ask mongodb and see how many plans do we have for requested task
        # task_plan = "PickUp: source_obj; Align: source_obj, destination_obj; Tilt: source_obj, PutDown: source_obj"
        #
        # TODO: It also infers the goal and populates the KB with correct goal statement, as well as the skill collection:
        # skill collection structure: {skill: str, skill_plan: str?, goal: str}

        # Close the MongoDB connection
        # client.close()

    def get_all_skills(self, field_name="skill_name"):
        cursor = collection.find({}, {field_name: 1})
        # Iterate over the query results
        for document in cursor:
            print(document[field_name])
        return document
    def get_type(self, obj):
        response = Prolog().ensure_once(f"""
                        kb_project([
                            findall([Type],(has_type({atom(obj)}, Type)), Type)
                        ]).
                    """)
        return response

    def add_skill_to_db(self, skill_name):
        # Sample JSON data for the document
        json_data = {
            "skill_name": skill_name
        }
        # Insert the skill into the skill collection after the task learning session is finished
        result = collection.insert_one(json_data)

        # Print the inserted document's ID
        print("Document inserted with ID:", result.inserted_id)

