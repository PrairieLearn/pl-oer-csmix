import itertools
import random
import math

"""utilities"""
import pathlib
import sys

from cs411 import * # tada
import json
import os

# Goals:
# Upon generation, check for serial schedules
# If serial, re-generate.

# After this, check whether the solution entails downgrading or deadlock, and compare those to options
# to determine whether to re-generate.

""" prairielearn code """

transaction_lookup = {"repeatable read":repeatable_read_scheduler,"read committed":read_committed_scheduler,"Two Phase Locking":two_phase_locking_scheduler,"Two Phase Locking (2PL)":two_phase_locking_downgrade_scheduler, "Strict Two Phase Locking (S2PL)":repeatable_read_scheduler}

def check_deadlock(sol):
    return sol[-1].type == 8 # WAIT
    
def check_downgrading(sol): # Check the solution for downgrading. Do we Sk(A) after we Xk(A)?
    fulls = set({})
    for a in sol:
        if a.type == 4: # Xlock
            fulls.add(f"{a.thread}, {a.attribute}")
        elif a.type == 3: # Slock
            if (f"{a.thread}, {a.attribute}" in fulls):
                return True
    return False

def check_serial(sch): # Easy enough, just check if the numbers are all in contiguous blocks.
    # A schedule is a list of actions with thread, type, and attribute.
    ct = sch[0].thread
    uts = set({})
    for a in sch:
        if (a.thread != ct):
            uts.add(ct)
            ct = a.thread
            if (ct in uts):
                return False
    return True
    
def check_desirable(data, sch, sol, _qconfig):
    data["params"]["isSerial"] = False
    data["params"]["hasDeadlock"] = False
    data["params"]["hasDowngrading"] = False
    serial = check_serial(sch)
    deadlock = check_deadlock(sol)
    downgrading = check_downgrading(sol)
    if (serial != _qconfig["serial"]):
        return False
    if (deadlock != _qconfig["deadlock"]):
        return False
    if (downgrading != _qconfig["downgrading"]):
        return False
    return True
    
def propose_schedule(data, _qconfig): # Generates a completely random schedule - no restrictions applied in this method.
    sched = generate_schedule(_qconfig["relation"],len(_qconfig["transactions"]),_qconfig["schedule_length"])
    sol = place_locks_and_wait(sched,[transaction_lookup[x] for x in _qconfig["transactions"]],_qconfig["relation"])
    return sched, sol
    
def generate(data):
    _qconfig_path = os.path.join(data["options"]["question_path"], "question_config.json")
    with open(_qconfig_path) as _qconfig_f:
        _qconfig = json.load(_qconfig_f)

    sched, sol = propose_schedule(data, _qconfig)
    while (not check_desirable(data, sched, sol, _qconfig)):
        sched, sol = propose_schedule(data, _qconfig)
    data["correct_answers"]["schedule"]=print_schedule(sol)
    data["params"]["schedule"]=print_schedule(sched)
    prot = _qconfig["transactions"][1]
    data["params"]["isolevels"]=" ".join([f"<li>The scheduler runs under the {prot} protocol.</li>"])
    data["params"]["relation"]=",".join(_qconfig["relation"])

def parse(data):
    try:
        data["submitted_answers"]["schedule"] = print_schedule(parse_schedule(data["raw_submitted_answers"]["schedule"]))
    except:
        data["format_errors"]["schedule"] = "Invalid syntax!"
