import sys
import ldb
import secrets
import string
from samba import samdb
from samba.auth import system_session
from samba.credentials import Credentials
from samba.param import LoadParm
from samba.samdb import SamDB
sys.path.append('.')
import backend_utils as u
__LIFECYLE_DIR__="../lifecycle"

def set_config(config):
    u.__CONFIG__ = config

def connect_sambaad(url,user,password):
    lp = LoadParm()
    creds = Credentials()
    creds.guess(lp)
    creds.set_username(user)
    creds.set_password(password)
    try:
        samdb = SamDB(url=url, session_info=system_session(),credentials=creds, lp=lp)
        result = samdb.search(
            base=u.config('base'),
            scope=ldb.SCOPE_BASE,
            attrs=["objectClass"]
        )
        return samdb
    except ldb.LdbError as e:
        code, message = e.args
        print(u.returncode(1,f"Erreur {code} : {message}"))
        exit(1)


def upsert_entry(samdb,entity):
    # test si l'entree existe
    result=search_entity(samdb,entity)
    if len(result) == 0:
        entry=u.make_entry_array_without_empty(entity)
        pwd=generate_password()
        try:
            uid=entry['uid']
            samdb.newuser(
                username=uid,
                givenname=entry['givenName'],
                surname=entry['sn'],
                mailaddress=entry['mail'],
                password=pwd
            )
            query = (f"(sAMAccountName={uid})")
            samdb.setexpiry(query,0,True)
            samdb.disable_account(query)
            return(u.returncode(0,'Entry added'))
        except ldb.LdbError as e:
            code, message = e.args
            print(u.returncode(1, f"Erreur {code} : {message}"))
            return (None)
    else:
        try:
            entry = result[0]
            msg = ldb.Message()
            msg.dn = entry.dn
            msg["sn"] = ldb.MessageElement(
                entry['sn'],
                ldb.FLAG_MOD_REPLACE,
                "sn"
            )
            msg["givenName"] = ldb.MessageElement(
                entry['givenName'],
                ldb.FLAG_MOD_REPLACE,
                "givenName"
            )
            msg["mail"] = ldb.MessageElement(
                entry['mail'],
                ldb.FLAG_MOD_REPLACE,
                "mail"
            )
            samdb.modify(msg)
            return (u.returncode(0, 'Entry modified'))
        except ldb.LdbError as e:
            code, message = e.args
            print(u.returncode(1, f"Erreur {code} : {message}"))
            return (None)


def search_entity(samdb,entity):
    uid = u.find_key(entity, 'uid')
    query = (f"(sAMAccountName={uid})")
    result=samdb.search(u.config('base'), expression=query, scope=ldb.SCOPE_SUBTREE)
    return (result)

def delete_entity(samdb,entity):
    uid = u.find_key(entity, 'uid')
    try:
        samdb.deleteuser(uid)
        return(u.returncode(0, 'Entry deleted'))
    except ldb.LdbError as e:
        code, message = e.args
        print(u.returncode(1, f"Erreur {code} : {message}"))
        return (None)

def activate_entry(samdb,entity,activate):
    uid = u.find_key(entity, 'uid')
    query = (f"(sAMAccountName={uid})")
    try:
        if activate == True:
            samdb.enable_account(query)
            return(u.returncode(0,'Entry activated'))
        else:
            samdb.disable_account(query)
            return(u.returncode(0,'Entry desactivated'))
    except ldb.LdbError as e:
        code, message = e.args
        print(u.returncode(1, f"Erreur {code} : {message}"))
        return (None)

def change_entity_password(samdb,entity):
    if 'oldPassword' in entity['payload'] and 'newPassword' in entity['payload']:
        oldPassword = entity['payload']['oldPassword']
        newPassword = entity['payload']['newPassword']
        if oldPassword != '' and newPassword != '':
            uid = u.find_key(entity, 'uid')
            # test ancien password
            if verify_password(uid,oldPassword) == 0:
                try:
                    query = (f"(sAMAccountName={uid})")
                    samdb.setpassword(query, newPassword, True)
                    return u.returncode(0, "Password for " + uid + " changed")
                except ldb.LdbError as e:
                    print(u.returncode(1, "Error entity_change_password"))
                    return (None)
    return(u.returncode(1, "Internal Error Error entity_change_password"))

def reset_entity_password(samdb,entity):
    if 'newPassword' in entity['payload']:
        try:
            newPassword = entity['payload']['newPassword']
            if newPassword != '':
                uid = u.find_key(entity, 'uid')
                query = (f"(sAMAccountName={uid})")
                samdb.setpassword(query, newPassword, True)
                return u.returncode(0, "Password for " + uid + " changed")
        except ldb.LdbError as e:
            code, message = e.args
            print(u.returncode(1, f"Erreur {code} : {message}"))
        return (None)
    return u.returncode(1, "Unexpected error")

def generate_password():
    longueur = 16
    chars = string.ascii_letters + string.digits + string.punctuation
    return( ''.join(secrets.choice(chars) for _ in range(longueur)) )

def verify_password(user,password):
    lp = LoadParm()
    creds = Credentials()
    creds.guess(lp)
    creds.set_username(user)
    creds.set_password(password)
    try:
        test = SamDB(url=u.config('host'), session_info=system_session(), credentials=creds, lp=lp)
        return 0
    except ldb.LdbError as e:
        code, message = e.args
        return (1)
def is_group_concerned(js):
    if u.config('groupFamily', '') == '':
        return True
    families = [f.strip() for f in u.config('groupFamily').split(',')]
    return js['payload']['group'].get('family', '') in families

def compare(listeSource,listeDestination):
    # add : valeurs presentes dans la source mais pas dans la destination
    # del : valeurs presentes dans la destination mais plus dans la source
    # comparaison insensible a la casse
    source = list(dict.fromkeys(v.lower() for v in listeSource))
    destination = list(dict.fromkeys(v.lower() for v in listeDestination))
    setSource = set(source)
    setDestination = set(destination)
    return {
        'add': [v for v in source if v not in setDestination],
        'del': [v for v in destination if v not in setSource]
    }

def getUid(samdb,dn):
    # renvoie le sAMAccountName correspondant au dn ou None
    try:
        res = samdb.search(base=dn, scope=ldb.SCOPE_BASE, attrs=["sAMAccountName"])
    except ldb.LdbError as e:
        return (None)
    if len(res) > 0 and "sAMAccountName" in res[0]:
        return str(res[0]["sAMAccountName"][0])
    return (None)

def do_group(samdb,entity):
    if not is_group_concerned(entity):
        return u.returncode(0, 'not concerned')
    #group exist ?
    query = (f"(&(cn={entity['payload']['group']['cn']})(objectclass=group))")
    base=u.config('base')
    result = samdb.search(base, expression=query, scope=ldb.SCOPE_SUBTREE)
    currentMembers=[]
    if (len(result) == 0):
        #add group
        try:
            samdb.newgroup(groupname=entity['payload']['group']['cn'])
        except ldb.LdbError as e:
            code, message = e.args
            return u.returncode(1, "Impossible de creer le groupe")
    else:
        for item in result:
            for member in item.get("member", []):
                # recherche de l'uid
                uid = getUid(samdb, str(member))
                if uid is not None:
                    currentMembers.append(uid)
    # gestion des utilisateurs dans le groupe
    members=[]
    for member in entity['payload']['members']:
        members.append(member['uid'])
    diff = compare(members, currentMembers)
    try:
        if len(diff['add']) > 0:
            samdb.add_remove_group_members(entity['payload']['group']['cn'],
                                       diff['add'],
                                       True)
        if len(diff['del']) > 0:
            samdb.add_remove_group_members(entity['payload']['group']['cn'],
                                       diff['del'],
                                       False)
    except ldb.LdbError as e:
        code, message = e.args
        return u.returncode(1, "Erreur groupe")
    return u.returncode(0, "OK")
