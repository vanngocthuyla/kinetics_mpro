import os
import numpy as np
import jax.numpy as jnp

import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

import arviz as az

from _kinetics import ReactionRate, MonomerConcentration, CatalyticEfficiency
from _model_mers import _dE_find_prior
from _MAP_finding_mers_concs import _extract_conc_lognormal


def plot_kinetics_data(experiments, params_logK, params_kcat, 
					   figure_size=(6.4, 4.8), dpi=80, OUTDIR=None): 
    """
    Parameters:
    ----------
    experiments : list of dict
        Each dataset contains response, logMtot, lotStot, logItot
    params_logK : dict of all dissociation constants
        logKd       : float, Log of the dissociation constant of dimerization
        logKd_MS_M  : float, Log of the dissociation constant between the monomer and substrate-monomer complex
        logK_S_M    : float, Log of the dissociation constant between the substrate and free monomer
        logK_S_D    : float, Log of the dissociation constant between the substrate and free dimer
        logK_S_DS   : float, Log of the dissociation constant between the substrate and ligand-dimer complex
        logKd_MI_M  : float, Log of the dissociation constant between the monomer and ligand-monomer complex
        logK_I_M    : float, Log of the dissociation constant between the inhibitor and free monomer
        logK_I_D    : float, Log of the dissociation constant between the inhibitor and free dimer
        logK_I_DI   : float, Log of the dissociation constant between the inhibitor and inhibitor-dimer complex
        logK_I_DS   : float, Log of the dissociation constant between the inhibitor and substrate-dimer complex
        logK_S_DI   : float, Log of the dissociation constant between the substrate and inhibitor-dimer complex
        All dissociation constants are in units of log molar
    params_kcat : dict of all kcat
        kcat_MS : float, Rate constant of monomer-substrate complex
        kcat_DS : float, Rate constant of dimer-substrate complex
        kcat_DSI: float, Rate constant of dimer-substrate-inhibitor complex
        kcat_DSS: float, Rate constant of dimer-substrate-substrate complex
    figure_size     : (width, height) size of plot
    dpi             : quality of plot
    OUTDIR          : optional, string, output directory for saving plot
    ----------
    return plots of each experiments
    """
    for n, experiment in enumerate(experiments):
        plt.figure(figsize=figure_size, dpi=dpi)
        try: 
            plt.title(f"{experiment['type']} from Fig. {experiment['figure']}")
        except: 
            pass
        x = experiment[experiment['x']]

        # Plot data
        if experiment['type']=='kinetics':
            plt.plot(x, experiment['v'], '.')
            plt.xlabel(experiment['x'])
            plt.ylabel('Rate (M min$^{-1}$)')
        elif experiment['type']=='AUC':
            plt.plot(x, experiment['M'], '.')
            plt.xlabel(experiment['x'])
            plt.ylabel('Monomer concentration (M)')
        elif experiment['type']=='catalytic_efficiency':
            plt.plot(x, experiment['Km_over_kcat'], '.')
            plt.xlabel(experiment['x'])
            plt.ylabel('K$_m$/k$_{cat}$')

        # Plot fit
        if experiment['x']=='logMtot':
            logMtot = np.linspace(experiment['logMtot'][0], experiment['logMtot'][-1], 50)
            logStot = experiment['logStot'][0]*np.ones(50)
            logItot = experiment['logItot'][0]*np.ones(50)
            x = logMtot
        elif experiment['x']=='logStot':
            logMtot = experiment['logMtot'][0]*np.ones(50)
            logStot = np.linspace(experiment['logStot'][0], experiment['logStot'][-1], 50)
            logItot = experiment['logItot'][0]*np.ones(50)
            x = logStot
        elif experiment['x']=='logItot':
            logMtot = experiment['logMtot'][0]*np.ones(50)
            logStot = experiment['logStot'][0]*np.ones(50)
            logItot = np.linspace(experiment['logItot'][0], experiment['logItot'][-1], 50)
            x = logItot

        if experiment['type']=='kinetics':
            y_model = ReactionRate(logMtot, logStot, logItot, *params_logK, *params_kcat)
        elif experiment['type']=='AUC':
            y_model = MonomerConcentration(logMtot, logStot, logItot, *params_logK)
        elif experiment['type']=='catalytic_efficiency':
            y_model = 1./CatalyticEfficiency(logMtot, logItot, *params_logK, *params_kcat)

        plt.plot(x, y_model)
        plt.tight_layout();

        if OUTDIR is not None: 
            plt.savefig(os.path.join(OUTDIR,f"{experiment['figure']}"))
            plt.ioff()


def plot_data_conc_log(experiments, params_logK, params_kcat, alpha_list=None, E_list=None,
                       outliers=None, line_colors=['blue', 'green', 'orange', 'purple', 'red'], ls='-',
                       fontsize_tick=10, fontsize_label=12,
                       fig_size=(5, 3.5), dpi=80, plot_legend=True, OUTFILE=None):
    """
    Parameters:
    ----------
    experiments : list of dict
        Each dataset contains response, logMtot, lotStot, logItot
    params_logK : dict of all dissociation constants
        logK_S_D    : float, Log of the dissociation constant between the substrate and free dimer
        logK_S_DS   : float, Log of the dissociation constant between the substrate and ligand-dimer complex
        logK_I_D    : float, Log of the dissociation constant between the inhibitor and free dimer
        logK_I_DI   : float, Log of the dissociation constant between the inhibitor and inhibitor-dimer complex
        logK_I_DS   : float, Log of the dissociation constant between the inhibitor and substrate-dimer complex
        logK_S_DI   : float, Log of the dissociation constant between the substrate and inhibitor-dimer complex
        All dissociation constants are in units of log molar
    params_kcat : dict of all kcat
        kcat_DS : float, Rate constant of dimer-substrate complex
        kcat_DSI: float, Rate constant of dimer-substrate-inhibitor complex
        kcat_DSS: float, Rate constant of dimer-substrate-substrate complex
    alpha           : optional, float or 1D array, normalization factor
    error_E         : optional, dict of enzyme concentration uncertainty
    figure_size     : (width, height) size of plot
    dpi             : quality of plot
    OUTDIR          : optional, string, directory for saving plot
    ----------
    return plots of each experiments with the concentration of inhibitor under log10 scale
    """    
    npoints=50
    plt.figure(figsize=fig_size, dpi=dpi)
    for i, experiment in enumerate(experiments):
        # plt.title(experiment['figure'])
        x = experiment[experiment['x']]

        # Plot data
        if experiment['type']=='kinetics':
            plt.plot(np.log10(np.exp(x)), experiment['v']*1E9, '.', color=line_colors[i])

        if outliers is not None and np.sum(outliers)>0:
            outlier = outliers[i]
            plt.plot(np.log10(np.exp(x[outlier])), experiment['v'][outlier]*1E9, color='r', ls=' ', marker='x', label='Outlier')

        # Plot fit
        if experiment['x']=='logMtot':
            logMtot = np.linspace(max(experiment['logMtot']), min(experiment['logMtot']), npoints)
            logStot = experiment['logStot'][0]*np.ones(npoints)
            logItot = experiment['logItot'][0]*np.ones(npoints)
            x = logMtot
        elif experiment['x']=='logStot':
            logMtot = experiment['logMtot'][0]*np.ones(npoints)
            logStot = np.linspace(max(experiment['logStot']), min(experiment['logStot']), npoints)
            if experiment['logItot'] is not None:
                logItot = experiment['logItot'][0]*np.ones(npoints)
            else:
                logItot = None
            x = logStot
        elif experiment['x']=='logItot':
            logMtot = experiment['logMtot'][0]*np.ones(npoints)
            logStot = experiment['logStot'][0]*np.ones(npoints)
            logItot = np.linspace(max(experiment['logItot']), min(experiment['logItot']), npoints) #9.95E-05
            x = logItot

        if experiment['type']=='kinetics':
            if E_list is not None:
                dE = _dE_find_prior([None, logMtot, logStot, logItot], E_list)
                logE = jnp.log(dE*1E-9)
            else: logE = logMtot

            if alpha_list is None:
                alpha = 1
            else:
                plate = experiment['plate']
                alpha = alpha_list[f'alpha:{plate}']

            y_model = ReactionRate(logE, logStot, logItot, *params_logK, *params_kcat)*alpha
            plt.plot(np.log10(np.exp(x)), y_model*1E9, ls=ls, color=line_colors[i], 
                     label=experiment['sub_figure'])

        if logItot is None:
            plt.xlabel('Log [S], M', fontsize=fontsize_label)
        else:
            plt.xlabel('Log ['+experiment['figure'][:12]+'], M', fontsize=fontsize_label)
        plt.ylabel('Rate (nM min$^{-1}$)', fontsize=fontsize_label)
        plt.xticks(fontsize=fontsize_tick)
        plt.yticks(fontsize=fontsize_tick)

        plt.tight_layout()
        if plot_legend:
            plt.legend()

        if OUTFILE is not None:
            plt.savefig(OUTFILE)


def plotting_trace_global(trace, out_dir, nchain=4, nsample=None, name_expts=None):
    """
    Parameters:
    ----------
    trace           : mcmc trace
    out_dir         : optional, string, directory for saving plot
    nchain          : optional, float, number of chains
    nsamples        : optional, float, number of samples in each chain
    name_expts      : list of string, name of experiments/datasets in the global fitting
    ----------
    return autocorrelation and trace plots of global fitting 
    """
    if name_expts is None:
        name_expts = ['ES', '00153', '00214', '00223', '00272', '00577', '00654', 
                      '00733', '00773', '08374', '08401', '08420', '08452', '08502']
    n_expts = len(name_expts)
    
    if nsample is None:
        keys = list(trace.keys())
        nsample = int(len(trace[keys[0]])/nchain)
    
    # Each ESI
    all_key_K_I = []
    for n in range(n_expts):
        trace_group = {}
        key_K_I = []
        for key in trace.keys():
            if key.startswith('logK_I_M') or key.startswith('logK_I_D') or key.startswith('logK_I_DI') or key.startswith('logK_S_DI') or key.startswith('kcat_DSI'):
                if key.endswith(":"+str(n)):
                    trace_group[key] = np.reshape(trace[key], (nchain, nsample))
                    key_K_I.append(key)
                    all_key_K_I.append(key)
        if len(key_K_I)>0:
            data = az.convert_to_inference_data(trace_group)
            az.plot_trace(data, compact=False)
            plt.tight_layout();
            plt.savefig(os.path.join(out_dir, 'Plot_trace_logK_I_'+str(n)))
            plt.close()

            az.plot_autocorr(trace, var_names=key_K_I);
            plt.savefig(os.path.join(out_dir, 'Plot_autocorr_logK_I_'+str(n)))
            plt.close()

    # Other logK
    trace_group = {}
    key_plot = []
    for key in trace.keys():
        if not key in all_key_K_I and key.startswith('logK'):
            trace_group[key] = np.reshape(trace[key], (nchain, nsample))
            key_plot.append(key)
    data = az.convert_to_inference_data(trace_group)
    az.plot_trace(data, compact=False)
    plt.tight_layout();
    plt.savefig(os.path.join(out_dir, 'Plot_trace_logK'))
    plt.close()

    az.plot_autocorr(trace, var_names=key_plot);
    plt.savefig(os.path.join(out_dir, 'Plot_autocorr_logK'))
    plt.close()

    # Other kcat
    trace_group = {}
    key_plot = []
    for key in trace.keys():
        if not key in all_key_K_I and key.startswith('kcat'):
            trace_group[key] = np.reshape(trace[key], (nchain, nsample))
            key_plot.append(key)
    data = az.convert_to_inference_data(trace_group)
    az.plot_trace(data, compact=False)
    plt.tight_layout();
    plt.savefig(os.path.join(out_dir, 'Plot_trace_kcat'))
    plt.close()

    az.plot_autocorr(trace, var_names=key_plot);
    plt.savefig(os.path.join(out_dir, 'Plot_autocorr_kcat'))
    plt.close()

    # Alpha, dE, I0
    for param_name in ['alpha', 'dE', 'I0']:
        trace_group = {}
        key_plot = []
        for key in trace.keys():
            if key.startswith(param_name):
                trace_group[key] = np.reshape(trace[key], (nchain, nsample))
                key_plot.append(key)
        if len(trace_group)>0:
            ## Trace plot
            data = az.convert_to_inference_data(trace_group)
            az.plot_trace(data, compact=False)
            plt.tight_layout();
            plt.savefig(os.path.join(out_dir, 'Plot_trace_'+param_name))
            plt.close()

            az.plot_autocorr(trace, var_names=key_plot);
            plt.savefig(os.path.join(out_dir, 'Plot_autocorr_'+param_name))
            plt.close()

    # Sigma
    for n in range(n_expts):
        trace_group = {}
        key_sigma = []
        for key in trace.keys():
            if key.startswith(f'log_sigma:{name_expts[n]}'):
                trace_group[key] = np.reshape(trace[key], (nchain, nsample))
                key_sigma.append(key)
        if len(trace_group)>0:
            data = az.convert_to_inference_data(trace_group)
            az.plot_trace(data, compact=False)
            plt.tight_layout();
            plt.savefig(os.path.join(out_dir, 'Plot_trace_sigma_'+str(n)))
            plt.close()

            az.plot_autocorr(trace, var_names=key_sigma);
            plt.savefig(os.path.join(out_dir, 'Plot_autocorr_sigma_'+str(n)))
            plt.close()


def plotting_trace(trace, out_dir, nchain=4, nsample=None):
    """
    Parameters:
    ----------
    trace           : mcmc trace
    out_dir         : optional, string, directory for saving plot
    nchain          : optional, float, number of chains
    nsamples        : optional, float, number of samples in each chain
    ----------
    return autocorrelation and trace plots of model fitting 
    """
    # Autocorrelation plot
    az.plot_autocorr(trace)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'Autocorrelation'))
    plt.ioff()
    
    # Trace plot
    if nsample is None:
        keys = list(trace.keys())
        nsample = int(len(trace[keys[0]])/nchain)

    if len(trace.keys())>=10:
        for param_name in ['logK', 'kcat', 'log_sigma', 'alpha', 'dE', 'I0']:
            trace_plot = {}
            for key in trace.keys():
                if key.startswith(param_name):
                    trace_plot[key] = np.reshape(trace[key], (nchain, nsample))
            if len(trace_plot)>0:
                data = az.convert_to_inference_data(trace_plot)
                az.plot_trace(data, compact=False)
                plt.tight_layout();
                plt.savefig(os.path.join(out_dir, 'Plot_trace_'+param_name))
                plt.ioff()
    else:
        trace_plot = {}
        for key in trace.keys():
            trace_plot[key] = np.reshape(trace[key], (nchain, nsample))
        data = az.convert_to_inference_data(trace_plot)
        az.plot_trace(data, compact=False)
        plt.tight_layout();
        plt.savefig(os.path.join(out_dir, 'Plot_trace'))
        plt.ioff()


# 1D Histogram
def _plot_1D_histogram(trace, param_list, outfile=None, hdi_prob=0.95, text_size=14, dpi=800):

    if len(param_list)<=4:
        ncol = len(param_list)
        fig, axs = plt.subplots(nrows=1, ncols=ncol, figsize=(ncol*2.5, 2.5))
        axs = axs.flatten()
    elif len(param_list)<=6:
        fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(7.5, 5))
        axs = axs.flatten()
        if len(param_list)==5:
            axs[5].axis("off")
    elif len(param_list)<=8:
        fig, axs = plt.subplots(nrows=2, ncols=4, figsize=(10, 5))
        axs = axs.flatten()
        if len(param_list)==7:
            axs[7].axis("off")

    for i, key in enumerate(param_list):
        trace_plot = {}
        trace_plot[key] = trace[key]
        az.plot_posterior(trace_plot, textsize=text_size, ax=axs[i], round_to=2, hdi_prob=hdi_prob)

    plt.tight_layout();
    if outfile is not None:
        plt.savefig(outfile, dpi=dpi, bbox_inches='tight');


def _plot_2D_histogram(data, param_list, dpi=800, label_size=20, tick_size=14, rotation_x=0, rotation_y=0,
                       outfile=None):

    N = len(param_list)-1

    fig, axis = plt.subplots(N, N, figsize=(N*2, N*2), constrained_layout=True,sharex=False, sharey=False)

    for i in range(len(param_list)-1): #col
        for j in range(1, len(param_list)): #row
            if i < j:
                az.plot_pair(data, var_names=[param_list[i], param_list[j]], ax=axis[j-1, i], divergences=False,
                            kind='kde', textsize=label_size)
                axis[j-1, i].tick_params(axis='x', labelrotation=rotation_x, labelsize=tick_size)
                axis[j-1, i].tick_params(axis='y', labelrotation=rotation_y, labelsize=tick_size)
                if j<N:
                    axis[j-1, i].xaxis.set_visible(False)
                if i>0:
                    axis[j-1, i].yaxis.set_visible(False)
            else:
                axis[j-1, i].set_visible(False)
    plt.tight_layout();

    if outfile is not None:
        plt.savefig(outfile, dpi=dpi);


def _heat_map(trace, params_list, outfile=None, fig_size=(6.4,4.8), dpi=800, 
              fontsize_tick=16, fontsize_text=12, nchain=4, niters=1000):
    
    plt.figure(figsize=fig_size)
    traces = {}
    for key in params_list:
        traces[key] = np.reshape(trace[key], (nchain, niters))
    data = az.convert_to_inference_data(traces)
    data_plot = az.InferenceData.to_dataframe(data)
    data_plot = data_plot.drop(['chain', 'draw'], axis=1)
    sns.heatmap(data_plot.corr(), annot=True, fmt="0.2f", linewidth=.5, annot_kws={"size": fontsize_text})
    plt.tick_params(labelsize=fontsize_tick)
    plt.tight_layout()
    if outfile is not None:
        plt.savefig(outfile, dpi=dpi, bbox_inches='tight');


#Linear correlation
def _linear_corr(xdata, ydata, xlabel, ylabel, outfile=None, fig_size=(4.25,3), dpi=800,
                 fontsize_label=20, fontsize_tick=16, fontsize_text=12, legend=False):
    
    plt.figure(figsize=fig_size)
    ax = plt.axes()
    res = stats.linregress(xdata, ydata)
    ax.plot(xdata, ydata, 'o', label='data')
    ax.plot(xdata, res.intercept + res.slope*xdata, 'k', label='Fitted line')
    ax.set_xlabel(xlabel, fontsize=fontsize_label)
    ax.set_ylabel(ylabel, fontsize=fontsize_label)
    if legend:
        plt.legend()
        ax.text(0.2, 0.9, ylabel+'='+str(round(res.slope, 2))+'*'+xlabel+'+'+str(round(res.intercept, 2)),
                fontsize=fontsize_text, transform=ax.transAxes);
    plt.xticks(fontsize=fontsize_tick)
    plt.yticks(fontsize=fontsize_tick)
    plt.tight_layout()
    if outfile is not None:
        plt.savefig(outfile, dpi=dpi, bbox_inches='tight');