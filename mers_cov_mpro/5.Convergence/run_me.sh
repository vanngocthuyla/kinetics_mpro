#!/bin/bash

export SCRIPT="/home/exouser/python/mers_mpro/scripts/run_trace_pymbar.py"

export MCMC_DIR="/home/exouser/python/mers_mpro/5.ESI/"

export OUT_DIR="/home/exouser/python/mers_mpro/5.Convergence/"

<<<<<<< HEAD
export N_INTER=10000
=======
export N_INTER=1000
>>>>>>> e16ad6bbbb4c64bfe977436054fce8235c94dbc0

export N_CHAIN=4

export KEY="logK_I_M logK_I_D logK_I_DI logK_S_DI kcat_DSI"

export TRACE_NAME='traces'

<<<<<<< HEAD
python $SCRIPT --mcmc_dir $MCMC_DIR --out_dir $OUT_DIR --niters $N_INTER --nchain $N_CHAIN --key_to_check "$KEY" --multi_expt --plotting --converged_trace_name $TRACE_NAME
=======
python $SCRIPT --mcmc_dir $MCMC_DIR --out_dir $OUT_DIR --niters $N_INTER --nchain $N_CHAIN --key_to_check "$KEY" --multi_expt --plotting --converged_trace_name $TRACE_NAME
>>>>>>> e16ad6bbbb4c64bfe977436054fce8235c94dbc0
