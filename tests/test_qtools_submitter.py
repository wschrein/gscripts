'''
Created on Aug 1, 2013

@author: Olga Botvinnik
'''
import unittest

from qtools import Submitter

import tests


class Test(unittest.TestCase):
    def test_main(self):
        commands = ['date', 'echo testing PBS']
        job_name = 'test_qtools_submitter'
        submit_sh = '%s.sh' % job_name
        sub = Submitter(queue_type='PBS', sh_file= submit_sh,
                        command_list=commands,
                        job_name=job_name)
        job_id = sub.write_sh(submit=True, nodes=1, ppn=16,
                                 queue='home-yeo', walltime='0:01:00')
        true_result = '''#!/bin/sh
#PBS -N test_qtools_submitter
#PBS -o test_qtools_submitter.out
#PBS -e test_qtools_submitter.err
#PBS -V
#PBS -l walltime=0:01:00
#PBS -l nodes=1:ppn=16
#PBS -A yeo-group
#PBS -q home-yeo
cd $PBS_O_WORKDIR
date
echo testing PBS'''.split('\n')


        for true, test in zip(true_result, open(tests.get_file(submit_sh))):
            self.assertEqual(true.strip().split(), test.strip().split())
        print 'job_id', job_id

    def test_wait_for_pbs(self):
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_main']
    unittest.main()