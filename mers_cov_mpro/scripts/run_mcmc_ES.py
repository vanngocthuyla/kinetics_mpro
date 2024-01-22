import warnings
import numpy as np
import sys
import os
import argparse

import pickle
import arviz as az
import pandas as pd

import jax
import jax.numpy as jnp
from jax import random
import jax.random as random

import numpyro
from numpyro.infer import MCMC, NUTS, init_to_value

import matplotlib.pyplot as plt

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter("ignore", UserWarning)
warnings.simplefilter("ignore", RuntimeWarning)

from _model_mers_ESI import global_fitting
from _load_data_mers import load_data_no_inhibitor
from _plotting import plot_data_conc_log, plotting_trace
from _MAP_finding_mers_concs import map_finding

from _prior_check import convert_prior_from_dict_to_list, check_prior_group
from _params_extraction import extract_logK_n_idx, extract_kcat_n_idx
from _trace_analysis import extract_params_from_map_and_prior

parser = argparse.ArgumentParser()

parser.add_argument( "--input_file",                    type=str,               default="")
parser.add_argument( "--out_dir",                       type=str, 				default="")
parser.add_argument( "--last_run_dir",                  type=str,               default="")
parser.add_argument( "--map_file",                      type=str,               default="")

parser.add_argument( "--fit_E_S",                       action="store_true",    default=False)
parser.add_argument( "--fit_E_I",                       action="store_true",    default=False)

parser.add_argument( "--multi_var",                     action="store_true",    default=False)
parser.add_argument( "--multi_alpha",                   action="store_true",    default=False)
parser.add_argument( "--set_lognormal_dE",              action="store_true",    default=False)
parser.add_argument( "--dE",                            type=float,             default=0.1)

parser.add_argument( "--set_K_S_DS_equal_K_S_D",        action="store_true",    default=False)
parser.add_argument( "--set_K_S_DI_equal_K_S_DS",       action="store_true",    default=False)

parser.add_argument( "--niters",				        type=int, 				default=10000)
parser.add_argument( "--nburn",                         type=int, 				default=2000)
parser.add_argument( "--nthin",                         type=int, 				default=1)
parser.add_argument( "--nchain",                        type=int, 				default=4)
parser.add_argument( "--random_key",                    type=int, 				default=0)

args = parser.parse_args()

from jax.config import config
config.update("jax_enable_x64", True)
numpyro.set_host_device_count(args.nchain)

print("ninter:", args.niters)
print("nburn:", args.nburn)
print("nchain:", args.nchain)
print("nthin:", args.nthin)

df_mers = pd.read_csv(args.input_file)
expts_no_I, expts_plot_no_I = load_data_no_inhibitor(df_mers, args.multi_var)

expts = expts_no_I

logKd_min = -20.72
logKd_max = 0.
kcat_min = 0.
kcat_max = 5.

prior = {}
prior['logKd'] = {'type':'logKd', 'name': 'logKd', 'fit':'global', 'dist': 'normal', 'loc': -9.9, 'scale': 0.5} 
prior['logK_S_M'] = {'type':'logK', 'name': 'logK_S_M', 'fit':'global', 'dist': 'uniform', 'lower': logKd_min, 'upper': logKd_max}
prior['logK_S_D'] = {'type':'logK', 'name': 'logK_S_D', 'fit':'global', 'dist': 'uniform', 'lower': logKd_min, 'upper': logKd_max}
prior['logK_S_DS'] = {'type':'logK', 'name': 'logK_S_DS', 'fit':'global', 'dist': 'uniform', 'lower': logKd_min, 'upper': logKd_max}

# prior['kcat_MS'] = {'type':'kcat', 'name': 'kcat_MS', 'fit':'global', 'dist': None, 'value': 0.}
prior['kcat_DS'] = {'type':'kcat', 'name': 'kcat_DS', 'fit':'global', 'dist': 'uniform', 'lower': kcat_min, 'upper': kcat_max}
prior['kcat_DSS'] = {'type':'kcat', 'name': 'kcat_DSS', 'fit':'global', 'dist': 'uniform', 'lower': kcat_min, 'upper': kcat_max}

shared_params = None

if args.set_K_S_DS_equal_K_S_D: 
    del prior['logK_S_DS']

pickle.dump(prior, open(os.path.join('Prior.pickle'), "wb"))
prior_infor = convert_prior_from_dict_to_list(prior, args.fit_E_S, args.fit_E_I)
prior_infor_update = check_prior_group(prior_infor, len(expts))
pd.DataFrame(prior_infor_update).to_csv("Prior_infor.csv", index=False)

print("Prior information: \n", pd.DataFrame(prior_infor_update))

if args.fit_E_S and args.fit_E_I: traces_name = "traces"
elif args.fit_E_S: traces_name = "traces_E_S"
elif args.fit_E_I: traces_name = "traces_E_I"

rng_key, rng_key_ = random.split(random.PRNGKey(args.random_key))
os.chdir(args.out_dir)

if not os.path.isfile(traces_name+'.pickle'):
    if len(args.map_file)>0 and os.path.isfile(args.map_file):
        init_values = pickle.load(open(args.map_file, "rb"))
        print("Initial values:", init_values)
        kernel = NUTS(model=global_fitting, init_strategy=init_to_value(values=init_values))
    else:
        kernel = NUTS(global_fitting)

    if os.path.isfile(os.path.join(args.last_run_dir, "Last_state.pickle")):
        last_state = pickle.load(open(os.path.join(args.last_run_dir, "Last_state.pickle"), "rb"))
        print("\nKeep running from last state.")
        mcmc = MCMC(kernel, num_warmup=args.nburn, num_samples=args.niters, num_chains=args.nchain, progress_bar=True)
        mcmc.post_warmup_state = last_state
        mcmc.run(mcmc.post_warmup_state.rng_key, experiments=expts, prior_infor=prior_infor_update, shared_params=shared_params,
                 multi_alpha=args.multi_alpha, set_lognormal_dE=args.set_lognormal_dE, dE=args.dE, 
                 multi_var=args.multi_var, set_K_S_DS_equal_K_S_D=args.set_K_S_DS_equal_K_S_D, set_K_S_DI_equal_K_S_DS=False)
    else:
        mcmc = MCMC(kernel, num_warmup=args.nburn, num_samples=args.niters, num_chains=args.nchain, progress_bar=True)
        mcmc.run(rng_key_, experiments=expts, prior_infor=prior_infor_update, shared_params=shared_params,
                 multi_alpha=args.multi_alpha, set_lognormal_dE=args.set_lognormal_dE, dE=args.dE, 
                 multi_var=args.multi_var, set_K_S_DS_equal_K_S_D=args.set_K_S_DS_equal_K_S_D, set_K_S_DI_equal_K_S_DS=False)
    mcmc.print_summary()

    print("Saving last state.")
    mcmc.post_warmup_state = mcmc.last_state
    pickle.dump(jax.device_get(mcmc.post_warmup_state), open("Last_state.pickle", "wb"))

    trace = mcmc.get_samples(group_by_chain=False)
    pickle.dump(trace, open(os.path.join(traces_name+'.pickle'), "wb"))

    plotting_trace(trace, args.out_dir, nchain=args.nchain, nsample=args.niters)

    trace = mcmc.get_samples(group_by_chain=True)
    az.summary(trace).to_csv(traces_name+"_summary.csv")

# Finding MAP
if os.path.isfile(traces_name+'.pickle'):
    trace = pickle.load(open(traces_name+'.pickle', "rb"))
else:
    trace = mcmc.get_samples(group_by_chain=False)

if shared_params is not None and len(shared_params)>0:
    for name in shared_params.keys():
        param = shared_params[name]
        assigned_idx = param['assigned_idx']
        shared_idx = param['shared_idx']
        trace[f'{name}:{assigned_idx}'] = trace[f'{name}:{shared_idx}']

[map_index, map_params, log_probs] = map_finding(trace, expts, prior_infor_update, 
                                                 set_lognormal_dE=args.set_lognormal_dE, dE=args.dE,  
                                                 set_K_S_DS_equal_K_S_D=args.set_K_S_DS_equal_K_S_D,
                                                 set_K_S_DI_equal_K_S_DS=False)

with open("map.txt", "w") as f:
    print("MAP index:" + str(map_index), file=f)
    print("\nKinetics parameters:", file=f)
    for key in trace.keys():
        print(key, ': %.3f' %trace[key][map_index], file=f)

pickle.dump(log_probs, open('log_probs.pickle', "wb"))

map_values = {}
for key in trace.keys():
    map_values[key] = trace[key][map_index]
pickle.dump(map_values, open('map.pickle', "wb"))

## Fitting plot
params_logK, params_kcat = extract_params_from_map_and_prior(trace, map_index, prior_infor_update)

for n in range(len(expts)):
    if args.set_K_S_DS_equal_K_S_D:
        try: params_logK[f'logK_S_DS:{n}'] = params_logK[f'logK_S_D:{n}']
        except: params_logK['logK_S_DS'] = params_logK['logK_S_D']

if args.set_lognormal_dE and args.dE>0:
    _error_E = {key: trace[key][map_index] for key in trace.keys() if key.startswith('dE')}
else: _error_E = None

n = 0
plot_data_conc_log(expts_plot_no_I, extract_logK_n_idx(params_logK, n, shared_params),
                   extract_kcat_n_idx(params_kcat, n, shared_params),
                   line_colors=['black', 'red', 'tab:brown'], ls='-.',
                   error_E=_error_E, plot_legend=True,
                   fontsize_tick=12, fontsize_label=18,
                   OUTFILE=os.path.join(args.out_dir,'ES'))