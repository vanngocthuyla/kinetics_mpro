#!/bin/bash

FILE=$(cd ../ && pwd)/'main_dir.txt'
DIR=$(<$FILE)

export SCRIPT='/kinetic_mpro/scripts/submit_mcmc_ESI.py'

export RUNNING_SCRIPT='/kinetic_mpro/scripts/run_mcmc_ESI_4_curves.py'

export INPUT='/kinetic_mpro/mers/input/ESI_mean_drop.csv'

export OUT_DIR='/kinetic_mpro/mers/3.ESI'

export PRIOR='/kinetic_mpro/mers/3.ESI/Prior.json'

export MAP_DIR='/kinetic_mpro/mers/2.ESI'

export N_INTER=1000

export N_BURN=200

export N_CHAIN=4

export NAME='ASAP-0000153 ASAP-0000214'

python $DIR$SCRIPT --input_file $DIR$INPUT --out_dir $DIR$OUT_DIR --running_script $DIR$RUNNING_SCRIPT --map_dir $DIR$MAP_DIR --prior_infor $DIR$PRIOR --niters $N_INTER --nburn $N_BURN --nchain $N_CHAIN --fit_E_S --fit_E_I --set_lognormal_dE --dE 0.5 --multi_var --name_inhibitor "$NAME"