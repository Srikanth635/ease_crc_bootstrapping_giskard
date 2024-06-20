#!/usr/bin/env python3
import sys
import os

sys.path.append(os.getcwd() + "/../")
from binder.rasa.scripts.intents import Intent
from binder.rasa.scripts.parse_instruction_rasa import query_rasa
from rosprolog_client import Prolog, atom
from pymongo import MongoClient
import json
import requests
import spacy

import subprocess
import sys



class BootstrapInterface:
    """
        Low-level interface to KnowRob, which enables the easy creation of NEEMs in Python.
        It provides bootstrapping predicates that can be used to create a task learning experience between teacher and a robot student
        """

    def __init__(self, mongo_interface):
        self.prolog = Prolog()
        self.mongo_interface = mongo_interface
        self.install_spacy_required_packages()
        self.nluServer = "http://localhost:5005/model/parse"
        self.spacyModel = "en_core_web_sm"
        self.nlp = spacy.load(self.spacyModel)
        self.placeholderWords = {"her", "him", "it", "them", "there"}


    def install_spacy_required_packages(self):
        packages = ['en_core_web_sm']
        for package_name in packages:
            if not spacy.util.is_package(package_name):
                subprocess.check_call([sys.executable, "-m", "spacy", "download", package_name])

    def parseIntent(self, text):
        req = {"text": text}
        r = requests.post(self.nluServer, data=bytes(json.dumps(req), "utf-8"))
        response = json.loads(r.text)
        retq = {"text": text, "UserIntent": response['intent']['name'], "entities": {}}
        for k, e in enumerate(response["entities"]):
            retq["entities"][k] = [e.get("role", "UndefinedRole"), e.get("value", "UnparsedEntity"), e.get("group", 0)]
        return retq

    def degroup(self, parses):
        retq = []
        for e in parses:
            intent = e["UserIntent"]
            entities = e["entities"]
            groups = {0: {}}
            for k, ed in entities.items():
                role, value, group = ed
                if group not in groups:
                    groups[group] = {}
                if role not in groups[group]:
                    groups[group][role] = set()
                groups[group][role].add((k, value))
            for k in sorted(groups.keys()):
                eds = {}
                for r, vs in groups[k].items():
                    for kk, v in vs:
                        eds[kk] = [r, v, 0]
                retq.append({"text": e["text"], "UserIntent": intent, "entities": eds})
        return retq

    def getSubtree(self, tok):
        inText = [(tok.idx, tok)]
        todo = list(tok.children)
        next = []
        while todo:
            cr = todo.pop()
            if ("VERB" == cr.pos_):
                next.append(cr)
            else:
                inText.append((cr.idx, cr))
                todo = todo + list(cr.children)
        toks = [str(x[1]) for x in sorted(inText, key=lambda x: x[0])]
        return next, ' '.join(toks)

    def splitIntents(self, text):
        doc = self.nlp(text)
        intentUtterances = []
        for s in doc.sents:
            todo = [s.root]
            while todo:
                cr = todo.pop()
                next, text = self.getSubtree(cr)
                todo = todo + next
                intentUtterances.append(text)
        return intentUtterances

    def guessRoles(self, parses, intent2Roles, role2Roles, needsGuessFn):
        def _te2de(entities):
            retq = {}
            for k, v in entities.items():
                role, value, _ = v
                if role not in retq:
                    retq[role] = set()
                retq[role].add(value)
            return retq

        def _de2te(self, entities):
            retq = {}
            j = 0
            for k, vs in entities.items():
                for v in vs:
                    retq[j] = (k, v, 0)
                    j += 1
            return retq

        roleMap = {}
        retq = []
        for e in parses:
            intent = e["UserIntent"]
            entities = _te2de(e["entities"])
            for role in intent2Roles[intent]:
                if needsGuessFn(entities.get(role, set())):
                    for guessedRole in {role}.union(role2Roles.get(role, [])):
                        if guessedRole in roleMap:
                            entities[role] = roleMap[guessedRole]
                            break
                elif 0 < len(entities.get(role, set())):
                    roleMap[role] = entities[role]
            retq.append({"text": e["text"], "UserIntent": intent, "entities": _de2te(entities)})
        return retq

    def semanticLabelling(self, text, intent2Roles, role2Roles, placeholderWords, missingRoleFn=None):
        intentUtterances = self.splitIntents(text)
        parsedIntents = self.degroup([self.parseIntent(x) for x in intentUtterances])
        parsedIntents = self.guessRoles((parsedIntents), intent2Roles, role2Roles,
                                   lambda x: 0 != len(x.intersection(placeholderWords)))
        for k, e in enumerate(parsedIntents):
            if (0 == len(e["entities"])) and (k < len(parsedIntents) - 1):
                j = 0
                for role, value, group in parsedIntents[k + 1]["entities"].values():
                    if role in intent2Roles[e["UserIntent"]]:
                        e["entities"][j] = (role, value, group)
                        j += 1
        return parsedIntents

    """
    * task_request: here the task request can be natural language sentence, we will parse this sentece and create a skill definition from it.
    * this method will have an interface will mongo skill collection which it will query to get the skill and plan from it.
    """

    def request(self, task_reqest: str):
        # Send the task request to RASA and get back the action core representation, and take action_verb and substance out and create a skill definition.
        action_core = query_rasa(task_reqest)
        if action_core:
            action_core['instruction'] = task_reqest

            # try to find skill with the keywords
            skills_found = self.find_skills(action_verb=action_core['action_verb'], goal=action_core['goal'])
            if not skills_found:
                response = "Sorry, I do not know how to " + action_core['goal'] + ". Can you show me how to do this?"
                print(response)
            return skills_found, action_core
        return None, None

    """
    """

    def save_action_core_to_db(self, action_core):
        # add action core to the mongodb skill collection
        document = self.mongo_interface.collection.insert_one(action_core)
        # Print the inserted document's ID
        print("Document inserted with ID:", document.inserted_id)
        return document

    def update_action_core(self, document):
        # Define the filter to find the document to update
        filter = {"_id": document['_id']}  # Example: Update the document with _id equal to 1

        # Define the update operation
        # update = {"$set": {"field_to_update": "new_value"}}  # Example: Update the field "field_to_update"

        # Update the document
        self.mongo_interface.collection.update_one(filter, document)

        print("Document updated successfully.")

    def find_skills(self, action_verb=None, goal=None):
        # Query documents for the specified field
        cursor = self.mongo_interface.collection.find({'action_verb': {'$regex': action_verb}, 'goal': goal})
        documents = []
        for document in cursor:
            if document:
                response = "Yes, I have found skill " + action_verb + " with goal: " + goal + "\n"
                print(response)
                documents.append(document)
        return documents

    def Perform(self, primitives: list):
        # TODO: use this predicate to build task plan, it should connect with giskard primitive motions
        # Create dictionary from list of primitives
        # self.action_core['task_plans'] = [{"primitive": primitive} for primitive in primitives]
        print("Performing task")

    def Explain(self):
        # TODO: use this predicate to explain the concept, it should connect with KG or Wordnet
        print("Explaining task")

    def Advice(self):
        # TODO: use this predicate to provide an advice for given primitive skill, it should connect to giskard and make necessary adjustments
        print("Advising for the task")

    """
        triple can be in the format of {sub: , pred: , obj:}
    """

    def Ask(self, triple: dict):
        # TODO: use this predicate to query the knowledge base from knowrob
        print("Asking the agent")

    def Demonstrate(self):
        # TODO: use this predicate to load VR neem from directory to knowrob
        print("Demonstrating the task to the agent")


class MongoDbInterface:
    def __init__(self):
        # Connect to MongoDB
        self.client = MongoClient('mongodb://localhost:27017/')
        # Create or access the database
        self.db = self.client['bootstrapping']

        # Create or access the collection
        self.collection = self.db['skills']

class KnowRobInterface(BootstrapInterface):

    def __init__(self):
        self.prolog = Prolog()

    def get_type(self, obj):
        response = Prolog().ensure_once(f"""
                        kb_project([
                            findall([Type],(has_type({atom(obj)}, Type)), Type)
                        ]).
                    """)
        return response


if __name__ == "__main__":
    mi = MongoDbInterface()
    bi = BootstrapInterface(mi)

    # 1. first set the task definition/instruction
    intents = bi.splitIntents("cut the cucumber with knife and serve it to Alice afterwards clean the table")
    print("intents:", intents)
    for intent in intents:
        documents_found, action_core = bi.request(intent)
        # print("skills found results: ", documents_found)
        print("rasa output results: ", action_core)

    # documents_found[0]['test'] = 'test'
    # # 2. Prompt user to change the rasa output if needed
    # for updating the document in mongodb one needs to use $set method which requires the field name and value. So think about this first.
    # bi.update_action_core(documents_found[0])

    bi.Perform(["pickup", "putdown"])
    # save rasa output once user agrees with the format
    # bi.add_skill_to_db()

    # testing the knowrob interface
    # ki = KnowRobInterface()
    # response =  ki.get_type('http://knowrob.org/kb/IAI-kitchen.owl#iai_kitchen_fridge_door_block')
    # print(response)
