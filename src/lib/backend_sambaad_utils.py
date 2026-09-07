import configparser
import json
import os
import jinja2
import sys
import getpass
import ldb
from samba.auth import system_session
from samba.credentials import Credentials
from samba.dcerpc import security
from samba.dcerpc.security import dom_sid
from samba.ndr import ndr_pack, ndr_unpack
from samba.param import LoadParm
from samba.samdb import SamDB
from sys import stdin
sys.path.append('.')
import backend_utils as u
__LIFECYLE_DIR__="../lifecycle"

def set_config(config):
    u.__CONFIG__ = config

def connect_sambaad(url,user,password):
    creds = Credentials()
    creds.guess(lp)
    creds.set_username(user)
    creds.set_password(password)
    try:
        samdb = SamDB(url=url, session_info=system_session(), credentials=creds, lp=lp)
        return (1)
    except samdb.error.SamDBError as e:
        print(u.returncode(1, e))
        return (1)

def upsert_entry(l,entity):
    return (1)

def search_entity(l,entity):
    return (1)

def delete_entity(l,entity):
    return (1)

def update_entity(l,entity):
    return (1)

def activate_entry(l,entity,activate):
    return (1)

def change_entity_password(l,entity):
    return (1)

def reset_entity_password(l,entity):
    return (1)



