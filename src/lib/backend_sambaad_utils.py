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
        return(None)


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
