import numpy as np
import arviz as az

def extract_samples_from_trace(trace, params, burn=0, thin=0):
    extract_samples = {}
    for var in params: 
      try:
          samples = np.concatenate(np.array(trace.posterior[var]))
          if burn!=0: 
              samples = samples[burn:]
          if thin!=0:
              samples = samples[::thin]
          extract_samples[var] = samples
      except:
          continue
    return extract_samples


def extract_params_from_trace_and_prior(trace, prior_infor):
    """
    Parameters:
    ----------
    trace        : mcmc.get_samples(group_by_chain=True)
    prior_infor  : list of dict of assigned prior distribution for kinetics parameters

    Example of prior_infor:
        [{'type': 'logKd', 'name': 'logKd',  'fit': 'local', 'dist': None, 'value': array([-11, -14])},
         {'type': 'logK','name': 'logK_S_M','fit': 'global','dist': 'uniform','lower': -20.0,'upper': 0.0}]
    ----------
    return two lists of kinetics parameters from trace and prior information
    """
    data = az.convert_to_inference_data(trace)
    params_name_kcat = []
    params_name_logK = []
    for name in trace.keys():
        if name.startswith('logK'):
            params_name_logK.append(name)
        if name.startswith('kcat'):
            params_name_kcat.append(name)

    samples_logK = extract_samples_from_trace(data, params_name_logK)
    samples_kcat = extract_samples_from_trace(data, params_name_kcat)
    params_logK = {}
    params_kcat = {}

    # Extract params from trace
    for name in params_name_logK:
        params_logK[name] = np.mean(samples_logK[name])
    for name in params_name_kcat:
        params_kcat[name] = np.mean(samples_kcat[name])    

    # Extract params from prior information
    for prior in prior_infor:
        if prior['dist'] is None:
            name = prior['name']
            if name.startswith('logK'):
                if prior['fit'] == 'local':
                    for n in range(len(prior['value'])):
                        params_logK[name+':'+str(n)] = prior['value'][n]
                else: params_logK[name] = prior['value']
            else:
                if prior['fit'] == 'local':
                    for n in range(len(prior['value'])):
                        params_kcat[name+':'+str(n)] = prior['value'][n]
                else: params_kcat[name] = prior['value']

    return params_logK, params_kcat


def list_kinetics_params(init_params, update_params):
    results = init_params
    for name_params in update_params:
        results[name_params] = update_params[name_params]
    return results