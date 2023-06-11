import numpy as np


def extract_logK(params_logK):
    """
    Parameters:
    ----------
    params_logK : dict of all dissociation constants
    ----------
    convert dictionary of dissociation constants to an array of values
    """
    # Dimerization
    if 'logKd' in params_logK.keys(): logKd = params_logK['logKd']
    else: logKd = None
    
    # Binding Substrate
    if 'logK_S_M' in params_logK.keys(): logK_S_M = params_logK['logK_S_M']
    else: logK_S_M = None
    if 'logK_S_D' in params_logK.keys(): logK_S_D = params_logK['logK_S_D']
    else: logK_S_D = None
    if 'logK_S_DS' in params_logK.keys(): logK_S_DS = params_logK['logK_S_DS']
    else: logK_S_DS = None
    
    # Binding Inhibitor
    if 'logK_I_M' in params_logK.keys(): logK_I_M = params_logK['logK_I_M']
    else: logK_I_M = None
    if 'logK_I_D' in params_logK.keys(): logK_I_D = params_logK['logK_I_D']
    else: logK_I_D = None
    if 'logK_I_DI' in params_logK.keys(): logK_I_DI = params_logK['logK_I_DI']
    else: logK_I_DI = None
    
    # Binding both substrate and inhititor
    if 'logK_S_DI' in params_logK.keys(): logK_S_DI = params_logK['logK_S_DI']
    else: logK_S_DI = None
    
    return [logKd, logK_S_M, logK_S_D, logK_S_DS, logK_I_M, logK_I_D, logK_I_DI, logK_S_DI]


def extract_kcat(params_kcat):
    """
    Parameters:
    ----------
    params_kcat : dict of all kcats
    ----------
    convert dictionary of kcats to an array of values
    """
    if 'kcat_MS' in params_kcat.keys(): kcat_MS = params_kcat['kcat_MS']
    else: kcat_MS = 0.
    if 'kcat_DS' in params_kcat.keys(): kcat_DS = params_kcat['kcat_DS']
    else: kcat_DS = 0.
    if 'kcat_DSI' in params_kcat.keys(): kcat_DSI = params_kcat['kcat_DSI']
    else: kcat_DSI = 0.
    if 'kcat_DSS' in params_kcat.keys(): kcat_DSS = params_kcat['kcat_DSS']
    else: kcat_DSS = 0.
    return [kcat_DS, kcat_DSI, kcat_DSS]


def extract_logK_n_idx(params_logK, idx):
    """
    Parameters:
    ----------
    params_logK : dict of all dissociation constants
    idx         : index of enzyme
    ----------
    convert dictionary of dissociation constants to an array of values depending on the index of enzyme
    
    """
    # Dimerization
    if f'logKd:{idx}' in params_logK.keys(): logKd = params_logK[f'logKd:{idx}']
    elif 'logKd' in params_logK.keys(): logKd = params_logK['logKd']
    else: logKd = None
    
    # Binding Substrate
    if f'logK_S_M:{idx}' in params_logK.keys(): logK_S_M = params_logK[f'logK_S_M:{idx}']
    elif 'logK_S_M' in params_logK.keys(): logK_S_M = params_logK['logK_S_M']
    else: logK_S_M = None    
    
    if f'logK_S_D:{idx}' in params_logK.keys(): logK_S_D = params_logK[f'logK_S_D:{idx}']
    elif 'logK_S_D' in params_logK.keys(): logK_S_D = params_logK['logK_S_D']
    else: logK_S_D = None
    
    if f'logK_S_DS:{idx}' in params_logK.keys(): logK_S_DS = params_logK[f'logK_S_DS:{idx}']
    elif 'logK_S_DS' in params_logK.keys(): logK_S_DS = params_logK['logK_S_DS']
    else: logK_S_DS = None
    
    # Binding Inhibitor
    if f'logK_I_M:{idx}' in params_logK.keys(): logK_I_M = params_logK[f'logK_I_M:{idx}']
    elif 'logK_I_M' in params_logK.keys(): logK_I_M = params_logK['logK_I_M']
    else: logK_I_M = None

    if f'logK_I_D:{idx}' in params_logK.keys(): logK_I_D = params_logK[f'logK_I_D:{idx}']
    elif 'logK_I_D' in params_logK.keys(): logK_I_D = params_logK['logK_I_D']
    else: logK_I_D = None

    if f'logK_I_DI:{idx}' in params_logK.keys(): logK_I_DI = params_logK[f'logK_I_DI:{idx}']
    elif 'logK_I_DI' in params_logK.keys(): logK_I_DI = params_logK['logK_I_DI']
    else: logK_I_DI = None
    
    # Binding both substrate and inhititor
    if f'logK_S_DI:{idx}' in params_logK.keys(): logK_S_DI = params_logK[f'logK_S_DI:{idx}']
    elif 'logK_S_DI' in params_logK.keys(): logK_S_DI = params_logK['logK_S_DI']
    else: logK_S_DI = None

    return [logKd, logK_S_M, logK_S_D, logK_S_DS, logK_I_M, logK_I_D, logK_I_DI, logK_S_DI]


def extract_kcat_n_idx(params_kcat, idx):
    """
    Parameters:
    ----------
    params_kcat : dict of all kcats
    idx         : index of enzyme
    ----------
    convert dictionary of kcats to an array of values depending on the index of enzyme
    """    
    if f'kcat_MS:{idx}' in params_kcat.keys(): kcat_MS=params_kcat[f'kcat_MS:{idx}'] 
    elif 'kcat_MS' in params_kcat.keys(): kcat_MS=params_kcat['kcat_MS']
    else: kcat_MS=0.
    
    if f'kcat_DS:{idx}' in params_kcat.keys(): kcat_DS = params_kcat[f'kcat_DS:{idx}'] 
    elif 'kcat_DS' in params_kcat.keys(): kcat_DS=params_kcat['kcat_DS']
    else: kcat_DS = 0.
    
    if f'kcat_DSI:{idx}' in params_kcat.keys(): kcat_DSI = params_kcat[f'kcat_DSI:{idx}'] 
    elif 'kcat_DSI' in params_kcat.keys(): kcat_DSI = params_kcat['kcat_DSI']
    else: kcat_DSI = 0.
    
    if f'kcat_DSS:{idx}' in params_kcat.keys(): kcat_DSS = params_kcat[f'kcat_DSS:{idx}'] 
    elif 'kcat_DSS' in params_kcat.keys(): kcat_DSS = params_kcat['kcat_DSS']
    else: kcat_DSS = 0.

    return [kcat_MS, kcat_DS, kcat_DSI, kcat_DSS]


def extract_logK_WT(params_logK):
    """
    Parameters:
    ----------
    params_logK : dict of all dissociation constants
    ----------
    convert dictionary of dissociation constants to an array of values
    """
    logK_S_D = params_logK['logK_S_D']
    logK_S_DS = params_logK['logK_S_DS']
    # Binding Inhibitor
    logK_I_D = params_logK['logK_I_D']
    logK_I_DI = params_logK['logK_I_DI']
    # Binding both substrate and inhititor
    if 'logK_S_DI' in params_logK.keys():
        logK_S_DI = params_logK['logK_S_DI']
    else: 
        logK_S_DI = None
    return [logK_S_D, logK_S_DS, logK_I_D, logK_I_DI, logK_S_DI]


def extract_kcat_WT(params_kcat):
    """
    Parameters:
    ----------
    params_kcat : dict of all kcats
    ----------
    convert dictionary of kcats to an array of values
    """
    kcat_DS = params_kcat['kcat_DS']
    if 'kcat_DSI' in params_kcat.keys():
        kcat_DSI = params_kcat['kcat_DSI']
    else:
        kcat_DSI = 0.
    kcat_DSS = params_kcat['kcat_DSS']
    return [kcat_DS, kcat_DSI, kcat_DSS]


def extract_logK_n_idx_WT(params_logK, idx):
    """
    Parameters:
    ----------
    params_logK : dict of all dissociation constants
    idx         : index of enzyme
    ----------
    convert dictionary of dissociation constants to an array of values depending on the index of enzyme
    """
    # Substrate Inhibitor
    if f'logK_S_D:{idx}' in params_logK.keys(): logK_S_D = params_logK[f'logK_S_D:{idx}']
    else: logK_S_D = params_logK['logK_S_D']
    if f'logK_S_DS:{idx}' in params_logK.keys(): logK_S_DS = params_logK[f'logK_S_DS:{idx}']
    else: logK_S_DS = params_logK['logK_S_DS']
    # Binding Inhibitor
    if f'logK_I_D:{idx}' in params_logK.keys(): logK_I_D = params_logK[f'logK_I_D:{idx}']
    else: logK_I_D = params_logK['logK_I_D']
    if f'logK_I_DI:{idx}' in params_logK.keys(): logK_I_DI = params_logK[f'logK_I_DI:{idx}']
    else: logK_I_DI = params_logK['logK_I_DI']
    # Binding both substrate and inhititor
    if f'logK_S_DI:{idx}' in params_logK.keys(): 
        logK_S_DI = params_logK[f'logK_S_DI:{idx}']
    elif 'logK_S_DI' in params_logK.keys(): 
        logK_S_DI = params_logK['logK_S_DI']
    else: 
        logK_S_DI = None
    return [logK_S_D, logK_S_DS, logK_I_D, logK_I_DI, logK_S_DI]


def extract_kcat_n_idx_WT(params_kcat, idx):
    """
    Parameters:
    ----------
    params_kcat : dict of all kcats
    idx         : index of enzyme
    ----------
    convert dictionary of kcats to an array of values depending on the index of enzyme
    """
    if f'kcat_DS:{idx}' in params_kcat.keys(): kcat_DS = params_kcat[f'kcat_DS:{idx}'] 
    else: kcat_DS = params_kcat['kcat_DS']
    if f'kcat_DSI:{idx}' in params_kcat.keys(): kcat_DSI = params_kcat[f'kcat_DSI:{idx}'] 
    elif 'kcat_DSI' in params_kcat.keys(): kcat_DSI = params_kcat['kcat_DSI']
    else: kcat_DSI = 0.
    if f'kcat_DSS:{idx}' in params_kcat.keys(): kcat_DSS = params_kcat[f'kcat_DSS:{idx}'] 
    else: kcat_DSS = params_kcat['kcat_DSS']
    return [kcat_DS, kcat_DSI, kcat_DSS]