import sys
import os
import glob
import argparse

parser = argparse.ArgumentParser()
parser.add_argument( "--out_dir",               type=str, 				default="")
# parser.add_argument( "--file_name",             type=str,               default="")

parser.add_argument( "--fit_mutant_kinetics",   action="store_true",    default=False)
parser.add_argument( "--fit_mutant_AUC",        action="store_true",    default=False)
parser.add_argument( "--fit_mutant_ICE",        action="store_true",    default=False)
parser.add_argument( "--fit_wildtype_Nashed",   action="store_true",    default=True)
parser.add_argument( "--fit_wildtype_Vuong",    action="store_true",    default=True)
parser.add_argument( "--fit_E_S",               action="store_true",    default=True)
parser.add_argument( "--fit_E_I",               action="store_true",    default=False)

parser.add_argument( "--niters",                type=int,               default=10000)
parser.add_argument( "--nburn",                 type=int,               default=2000)
parser.add_argument( "--nthin",                 type=int, 				default=1)
parser.add_argument( "--nchain",                type=int, 				default=4)
parser.add_argument( "--random_key",            type=int, 				default=0)

args = parser.parse_args()

running_script = "/home/exouser/python/mpro/scripts/run_mcmc_multi_enzymes.py"

if args.fit_E_S and args.fit_E_I:
    file_name = "combined"
elif args.fit_E_S: 
    file_name = "combined_E_S"
elif args.fit_E_I: 
    file_name = "combined_E_I"

if args.fit_mutant_kinetics: 
    fit_mutant_kinetics = " --fit_mutant_kinetics "
else:
    fit_mutant_kinetics = " "

if args.fit_mutant_AUC: 
    fit_mutant_AUC = " --fit_mutant_AUC "
else:
    fit_mutant_AUC = " "

if args.fit_mutant_ICE:
    fit_mutant_ICE = " --fit_mutant_ICE "
else:
    fit_mutant_ICE = " "

if args.fit_wildtype_Nashed:
    fit_wildtype_Nashed = " --fit_wildtype_Nashed "
else:
    fit_mutant_kinetics = " "

if args.fit_wildtype_Vuong: 
    fit_wildtype_Vuong = " --fit_wildtype_Vuong "
else:
    fit_wildtype_Vuong = " "

if args.fit_E_S: 
    fit_E_S = " --fit_E_S "
else:
    fit_E_S = " "

if args.fit_E_I: 
    fit_E_I = " --fit_E_I "
else:
    fit_E_I = " "

qsub_file = os.path.join(args.out_dir, file_name+".job")
log_file  = os.path.join(args.out_dir, file_name+".log")

qsub_script = '''#!/bin/bash
#PBS -S /bin/bash
#PBS -o %s '''%log_file + '''
#PBS -j oe
#PBS -l nodes=1:ppn=1,mem=8192mb,walltime=720:00:00

module load miniconda/3
source activate bitc_race
cd ''' + args.out_dir + '''\n''' + \
    '''date\n''' + \
    '''python ''' + running_script + \
    ''' --out_dir ''' + args.out_dir + \
    fit_mutant_kinetics + fit_mutant_AUC + fit_mutant_ICE + \
    fit_wildtype_Nashed + fit_wildtype_Vuong + fit_E_S + fit_E_I + \
    ''' --niters %d '''%args.niters + \
    ''' --nburn %d '''%args.nburn + \
    ''' --nthin %d '''%args.nthin + \
    ''' --nchain %d '''%args.nchain + \
    ''' --random_key %d '''%args.random_key + \
    '''\ndate \n''' 

print("Submitting " + qsub_file)
open(qsub_file, "w").write(qsub_script)
#os.system("qsub %s"%qsub_file)