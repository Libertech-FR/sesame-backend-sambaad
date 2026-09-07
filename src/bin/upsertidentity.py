#!/usr/bin/python3
import sys
sys.path.append('../lib')
import backend_utils as u
import backend_sambaad_utils as smb


def main():
    json=u.readjsoninput()
    config=u.read_config('../etc/config.conf')
    smb.set_config(config)
    if u.is_backend_concerned(json):
        l=smb.connect_sambaad(u.config('host'),u.config('dn'),u.config('password'))
        print(smb.upsert_entry(l,json))
    else:
        print(u.returncode(0,'not concerned'))


if __name__ == '__main__':
    main()
