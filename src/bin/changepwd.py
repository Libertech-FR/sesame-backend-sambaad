#!/usr/bin/python3
import sys
sys.path.append('../lib')
import backend_sambaad_utils as smb
import backend_utils as u
import json
def main():
    js=u.readjsoninput()
    config= u.read_config('../etc/config.conf')
    smb.set_config(config)
    if u.is_backend_concerned(js):
        l=smb.connect_sambaad(u.config('host'),u.config('user'),u.config('password'))
        ret=smb.change_entity_password(l,js)
        result=json.loads(ret)
        print(ret)
        exit(result['status'])
    else:
        print(u.returncode(0,'not concerned'))

if __name__ == '__main__':
    main()

