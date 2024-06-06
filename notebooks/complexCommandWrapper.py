import json
import requests
import spacy

import subprocess
import sys

def install_spacy_required_packages():
    packages = ['en_core_web_sm']
    for package_name in packages:
        if not spacy.util.is_package(package_name):
            subprocess.check_call([sys.executable, "-m", "spacy", "download", package_name])

install_spacy_required_packages()

nluServer = "http://localhost:5005/model/parse"
spacyModel = "en_core_web_sm"

nlp=spacy.load(spacyModel)

placeholderWords = {"her", "him", "it", "them", "there"}

def parseIntent(text):
    req = {"text": text}
    r = requests.post(nluServer,  data=bytes(json.dumps(req), "utf-8"))
    response = json.loads(r.text)
    retq = {"text": text, "UserIntent": response['intent']['name'], "entities": {}}
    for k,e in enumerate(response["entities"]):
        retq["entities"][k] = [e.get("role", "UndefinedRole"), e.get("value", "UnparsedEntity"), e.get("group", 0)]
    return retq
    
def degroup(parses):
    retq=[]
    for e in parses:
        intent=e["UserIntent"]
        entities=e["entities"]
        groups={0:{}}
        for k, ed in entities.items():
            role,value,group=ed
            if group not in groups:
                groups[group]={}
            if role not in groups[group]:
                groups[group][role]=set()
            groups[group][role].add((k, value))
        for k in sorted(groups.keys()):
            eds = {}
            for r,vs in groups[k].items():
                for kk,v in vs:
                    eds[kk]= [r,v,0]
            retq.append({"text":e["text"], "UserIntent":intent, "entities": eds})
    return retq

def getSubtree(tok):
    inText=[(tok.idx, tok)]
    todo=list(tok.children)
    next = []
    while todo:
        cr=todo.pop()
        if ("VERB" == cr.pos_):
            next.append(cr)
        else:
            inText.append((cr.idx,cr))
            todo = todo + list(cr.children)
    toks = [str(x[1]) for x in sorted(inText,key=lambda x:x[0])]
    return next, ' '.join(toks)

def splitIntents(text):
    doc=nlp(text)
    intentUtterances=[]
    for s in doc.sents:
        todo=[s.root]
        while todo:
            cr = todo.pop()
            next, text = getSubtree(cr)
            todo = todo+next
            intentUtterances.append(text)
    return intentUtterances

def guessRoles(parses, intent2Roles, role2Roles, needsGuessFn):
    def _te2de(entities):
        retq = {}
        for k,v in entities.items():
            role,value,_=v
            if role not in retq:
                retq[role]=set()
            retq[role].add(value)
        return retq
    def _de2te(entities):
        retq={}
        j=0
        for k,vs in entities.items():
            for v in vs:
                retq[j] = (k,v,0)
                j += 1
        return retq
    roleMap={}
    retq=[]
    for e in parses:
        intent=e["UserIntent"]
        entities=_te2de(e["entities"])
        for role in intent2Roles[intent]:
            if needsGuessFn(entities.get(role,set())):
                for guessedRole in {role}.union(role2Roles.get(role,[])):
                    if guessedRole in roleMap:
                        entities[role]=roleMap[guessedRole]
                        break
            elif 0<len(entities.get(role,set())):
                roleMap[role]=entities[role]
        retq.append({"text":e["text"],"UserIntent":intent,"entities":_de2te(entities)})
    return retq

def semanticLabelling(text, intent2Roles, role2Roles, placeholderWords, missingRoleFn=None):
    intentUtterances=splitIntents(text)
    parsedIntents=degroup([parseIntent(x) for x in intentUtterances])
    parsedIntents=guessRoles((parsedIntents), intent2Roles, role2Roles, lambda x: 0!=len(x.intersection(placeholderWords)))
    for k,e in enumerate(parsedIntents):
        if (0==len(e["entities"])) and (k < len(parsedIntents)-1):
            j=0
            for role, value, group in parsedIntents[k+1]["entities"].values():
                 if role in intent2Roles[e["UserIntent"]]:
                     e["entities"][j] = (role,value,group)
                     j+=1
    return parsedIntents

