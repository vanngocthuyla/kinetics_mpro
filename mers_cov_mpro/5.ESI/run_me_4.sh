#!/bin/bash

export SCRIPT="/home/exouser/python/mers_mpro/scripts/submit_mcmc_ESI.py"

export INPUT="/home/exouser/python/mers_mpro/input/ESI_mean_drop.csv"

export OUT_DIR="/home/exouser/python/mers_mpro/5.ESI/sampling_4"

export MAP_DIR="/home/exouser/python/mers_mpro/5.ESI/sampling_1"

export MAP_NAME="map_sampling.pickle"

export LAST_RUN_DIR="/home/exouser/python/mers_mpro/5.ESI/sampling_3"

export RUNNING_SCRIPT="/home/exouser/python/mers_mpro/scripts/run_mcmc_ESI_fixed_ES.py"

export INHIBITOR_NAMES="ASAP-0000153"

export N_INTER=2000

export N_BURN=200

export N_CHAIN=4

python $SCRIPT --input_file $INPUT --out_dir $OUT_DIR --running_script $RUNNING_SCRIPT --niters $N_INTER --nburn $N_BURN --nchain $N_CHAIN --fit_E_S --fit_E_I --dE 0 --multi_var --multi_alpha --map_dir $MAP_DIR --map_name $MAP_NAME --last_run_dir $LAST_RUN_DIR --name_inhibitor "$INHIBITOR_NAMES"
