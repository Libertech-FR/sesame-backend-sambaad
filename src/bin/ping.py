#!/usr/bin/python3
import sys
import ldb
sys.path.append('../lib')
import backend_sambaad_utils as smb
import backend_utils as u
def main():
    config=u.read_config('../etc/config.conf')
    smb.set_config(config)
    samdb = smb.connect_sambaad(u.config('host'), u.config('user'), u.config('password'))
    if samdb:
        print(u.returncode(0,'I m alive'))
        return 0


if __name__ == '__main__':
    main()