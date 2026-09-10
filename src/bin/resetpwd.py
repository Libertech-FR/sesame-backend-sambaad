#!/usr/bin/python3
import sys
sys.path.append('../lib')
import backend_sambaad_utils as smb
import backend_utils as u

def main():
    json=u.readjsoninput()
    config=u.read_config('../etc/config.conf')
    smb.set_config(config)
    if u.is_backend_concerned(json):
        l=smb.connect_sambaad(u.config('host'),u.config('user'),u.config('password'))
        print(smb.reset_entity_password(l,json))
    else:
        print(u.returncode(0,'not concerned'))


if __name__ == '__main__':
    main()