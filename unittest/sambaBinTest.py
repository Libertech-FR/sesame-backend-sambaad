import unittest
import subprocess
import os
import json
__PYTHONENV__='/usr/bin/python3'
class sambaBinTest (unittest.TestCase):
    def run_backend(self,script, file= "",args=""):
        dir = os.getcwd()
        exe=__PYTHONENV__
        execargs=[]
        execargs.append(exe)
        execargs.append(script)
        if args :
            execargs.append(args)
        if file == '':
            os.chdir('../src/bin')
            ret = subprocess.run(execargs,capture_output=True)
        else:
            #open file to pass to stdin
            fic = open(file, "r")
            content = fic.read()
            content = content.replace("\n", "")
            fic.close()
            os.chdir('../src/bin')
            ret = subprocess.run(execargs,input=content.encode(),capture_output=True)
        os.chdir(dir)
        return { "returncode" : ret.returncode,"stdout" : ret.stdout.decode()}
    def test_01ping(self):
        ret = self.run_backend('ping.py','')
        self.assertEqual(ret['returncode'],0)
        result=json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "I m alive")

    def test_02upsert_add(self):
        ret = self.run_backend('upsertidentity.py', './backend_ad_files/identity1.json')
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "Entry added")

    def test_02upsert_mod(self):
        ret = self.run_backend('upsertidentity.py', './backend_ad_files/identity1.json')
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "Entry modified")

    def test_03resetpwd(self):
        ret = self.run_backend('resetpwd.py', './backend_ad_files/resetpassword.json')
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "Password for omaton changed")

    def test_04changepwd_true(self):
        ret = self.run_backend('changepwd.py', './backend_ad_files/changepassword_true.json')
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "Password for omaton changed")

    def test_05changepwd_false(self):
        ret = self.run_backend('changepwd.py', './backend_ad_files/changepassword_true.json')
        self.assertEqual(ret['returncode'], 1)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 1)
        self.assertEqual(result["message"], "Internal Error Error entity_change_password")

    def test_06activate(self):
        ret = self.run_backend('activation.py', './backend_ad_files/identity1.json', "--active=1")
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "Identity enabled")

    def test_07desactivate(self):
        ret = self.run_backend('activation.py', './backend_ad_files/identity1.json',"--active=0")
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "Identity disabled")

    def test_09delentity(self):
        ret = self.run_backend('delentity.py', './backend_ad_files/identity1.json')
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "Entry deleted")



if __name__ == '__main__':
    unittest.main()
