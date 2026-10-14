import sys
import ldb
sys.path.append('../lib')
import backend_utils as u
import backend_sambaad_utils as smb


def main():
    json=u.readjsoninput()
    #json=u.readjsonfile('../../unittest/backend_ad_files/identity1.json')
    config=u.read_config('../etc/config.conf')
    smb.set_config(config)
    l=smb.connect_sambaad(u.config('host'),u.config('user'),u.config('password'))
    ret=smb.do_group(l,json)
    print(ret)

if __name__ == '__main__':
    main()