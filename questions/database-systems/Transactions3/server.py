import itertools
import random
import math

"""utilities"""
import pathlib
import sys

from cs411 import * # tada
import json
import os

""" prairielearn code """

transaction_lookup = {"repeatable read":repeatable_read_scheduler,"read committed":read_committed_scheduler}

def verify(sched):
    if (sched == False):
        return False
    t = set() 
    for s in sched: # Get the number of this Action (Action class has thread, type, and attribute)
        t.add(s.thread)
    return len(t) > 1

def generate(data):
    _qconfig_path = os.path.join(data["options"]["question_path"], "question_config.json")
    with open(_qconfig_path) as _qconfig_f:
        _qconfig = json.load(_qconfig_f)

    relation = _qconfig["relation"]
    transactions = _qconfig["transactions"]
    sched = False
    while verify(sched) == False:
        sched = generate_schedule(relation,len(transactions),_qconfig["schedule_length"])
    data["correct_answers"]["schedule"]=print_schedule(place_locks(sched,[transaction_lookup[x] for x in transactions],relation))
    data["params"]["schedule"]=print_schedule(sched)
    data["params"]["isolevels"]=" ".join([f"<li>Transaction {x+1} has isolation level {transactions[x]}.</li>" for x in range(len(transactions))])
    data["params"]["relation"]=",".join(_qconfig["relation"])

def parse(data):
    try:
        data["submitted_answers"]["schedule"] = print_schedule(parse_schedule(data["raw_submitted_answers"]["schedule"]))
    except:
        data["format_errors"]["schedule"] = "Invalid syntax!"