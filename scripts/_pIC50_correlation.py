import numpy as np
import os
import pandas as pd

import scipy
from scipy import stats
from scipy.optimize import curve_fit

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

from _chemical_reactions import ChemicalReactions
from _pIC50 import f_pIC90, _pd_mean_std_pIC


def _wm(x, w):
    """Weighted Mean"""
    return np.sum(x * w) / np.sum(w)


def _cov(x, y, w):
    """Weighted Covariance"""
    return np.sum(w * (x - _wm(x, w)) * (y - _wm(y, w))) / np.sum(w)


def _corr(x, y, w):
    """Weighted Correlation"""
    return _cov(x, y, w) / np.sqrt(_cov(x, x, w) * _cov(y, y, w))


def corr_matrix(data, keys, method='pearsonr'):
    """
    Input: dataframe
    Keys: column names of dataframe to calculate correlation coefficients
    Params:
        The method to calculate correlation coefficients can be 'pearsonr', 'spearmanr' or 'kendall'
    """
    table = pd.DataFrame(columns=keys, index=range(len(keys)))
    for i in range(1, len(keys)):
        for j in range(i):
            # x = pd.DataFrame.to_numpy(data[keys[i]])
            x = data[keys[i]]
            # y = pd.DataFrame.to_numpy(data[keys[j]])
            y = data[keys[j]]
            dat = pd.DataFrame([x, y], index=['X', 'Y']).T
            dat = dat.dropna()
            if len(dat)>2:
                #Calculate the correlation
                if method=='pearsonr':
                    coef, p = stats.pearsonr(dat.X, dat.Y)
                if method=='spearmanr':
                    coef, p = stats.spearmanr(dat.X, dat.Y)
                if method=='kendall':
                    coef, p = stats.kendalltau(dat.X, dat.Y)
                text = r'n=' +str(len(dat)) +'; r=' +str('%5.3f' %coef) +'; p=' +str('%5.3e' %p)
            else:
                text = r'n=' +str(len(dat))
            table.iloc[i][keys[j]] = text
    # table = table.rename(index={0: "Fluorescence", 1: "Antiviral_Leuven", 2: "Antiviral_Zitzman", 3: "Antiviral_Takeda", 4: "Antiviral_IIBR"})
    return table


def rmsd_matrix(data, keys, method='RMSD'):
    """
    Parameters
    ----------
    data        : dataset contains the set of variables for correlation analysis
    keys        : column names of dataframe to calculate correlation coefficients
    method      : the method to calculate RMSD, can be 'RMSD', or 'aRMSD'

    return the RMSD given two datasets of two variables
    """
    table = pd.DataFrame(columns=keys, index=range(len(keys)))
    for i in range(1, len(keys)):
        for j in range(i):
            # x = pd.DataFrame.to_numpy(data[keys[i]])
            x = data[keys[i]]
            # y = pd.DataFrame.to_numpy(data[keys[j]])
            y = data[keys[j]]
            dat = pd.DataFrame([x, y], index=['X', 'Y']).T
            dat = dat.dropna()
            if len(dat)>2:
                if method=='RMSD':
                    rmsd = np.sqrt(np.mean((dat.X - dat.Y)**2))
                elif method == 'aRMSD':
                    rmsd = np.sqrt(np.mean((dat.X - dat.Y - (np.mean(dat.X) - np.mean(dat.Y)))**2))
                text = r'n=' +str(len(dat)) +'; r=' +str('%5.3f' %rmsd)
            else:
                text = r'n=' +str(len(dat))
            table.iloc[i][keys[j]] = text
    return table


def corr_pearsonr_N_sample(x, y, ax=None, **kwargs):
    """
    Parameters
    ---------- 
    x           : pd.DataFrams, dataset of one variable
    y           : pd.DataFrams, dataset of other variable

    Return the correlation coefficients of two panda dataframes in the correlogram
    """

    #Remove the NaN data
    data = pd.DataFrame([x, y], index=['X', 'Y']).T
    data = data.dropna()
    if len(data)>2:
        #Calculate the correlation
        coef, p = stats.pearsonr(data.X, data.Y)
        #Make the label
        label = r'r=' + str('%5.3f' %coef) + '; p=' + str('%5.3e' %p) + '\nN=' + str(len(data))
    else:
        #Make the label
        label = 'nan'
    #count how many annotations are already present and add the label to the plot
    if ax is None:
        ax = plt.gca()
    n = len([c for c in ax.get_children() if isinstance(c, matplotlib.text.Annotation)])
    pos = (.1, .8 - .1*n)
    colors = ['blue','orange']
    ax.annotate(label, xy=pos, xycoords=ax.transAxes, color=colors[n])


def _corr_coef(x, y, method='pearsonr'):
    """
    Parameters
    ----------
    x           : numpy.array, datasets of one variable
    y           : numpy.array, datasets of other variable
    method      : The method to calculate correlation coefficients can be 'pearsonr', 'spearmanr', 'kendall', 'RMSD', or 'aRMSD'

    return the correlation given two datasets of two variables
    """
    if method=='pearsonr':
        corr, p = stats.pearsonr(x, y)
    elif method=='spearmanr':
        corr, p = stats.spearmanr(x, y)
    elif method=='kendall':
        corr, p = stats.kendalltau(x, y)
    elif method=='RMSD':
        corr = np.sqrt(np.mean((x - y)**2))
        p = None
    elif method == 'aRMSD':
        corr = np.sqrt(np.mean((x - y - (np.mean(x) - np.mean(y)))**2))
        p = None
    return corr, p


def corr_bootstrap(x, y, n_bootstrap=100, method='pearsonr'):
    """
    Parameters
    ----------
    x           : numpy.array, dataset of one variable
    y           : numpy.array, dataset of other variable
    n_bootstrap : Number of bootstrap samples
    method      : The method to calculate correlation coefficients can be 'pearsonr', 'spearmanr', 'kendall', 'RMSD', or 'aRMSD'

    return the correlation given a dataset consists of paired observations where each (x_i, y_i) pair is related to each other
    """
    dat = pd.DataFrame([x, y], index=['X', 'Y']).T
    dat = dat.dropna()
    x = np.array(dat.X)
    y = np.array(dat.Y)
    bootstrap_correlations = []
    for _ in range(n_bootstrap):
        # Generate random indices with replacement
        indices = np.random.choice(len(x), size=len(y), replace=True)

        # Select corresponding elements from both x and y arrays
        resampled_x = x[indices]
        resampled_y = y[indices]

        # Calculate correlation coefficient
        corr, p = _corr_coef(x, y, method)
        bootstrap_correlations.append(corr)

        # Analyze the distribution
        mean_corr = np.mean(bootstrap_correlations)
        std_corr = np.std(bootstrap_correlations)
        # confidence_interval = np.percentile(bootstrap_correlations, [2.5, 97.5])

    return mean_corr, std_corr


def corr_bootstrap_matrix(data, keys, n_bootstrap=100, method='pearsonr'):
    """
    Parameters
    ----------
    data        : dataset contains the set of variables for correlation analysis
    keys        : column names of dataframe to calculate correlation coefficients
    method      : The method to calculate correlation coefficients can be 'pearsonr', 'spearmanr', 'kendall', 'RMSD', or 'aRMSD'
    """
    table = pd.DataFrame(columns=keys, index=range(len(keys)))
    for i in range(1, len(keys)):
        for j in range(i):
            # x = pd.DataFrame.to_numpy(data[keys[i]])
            x = data[keys[i]]
            # y = pd.DataFrame.to_numpy(data[keys[j]])
            y = data[keys[j]]
            if len(dat)>2:
                mean_corr, std_corr = corr_bootstrap(x, y, n_bootstrap, method)
                text = r'n=' +str(len(x)) +'; corr=' +str('%5.3f' %mean_corr) +' ± ' +str('%5.3e' %std_corr)
            else:
                text = r'n=' +str(len(x))
            table.iloc[i][keys[j]] = text
    return table


def corr_leave_p_out(x, y, p=2, method='pearsonr'):
    """
    Parameters
    ----------
    x           : numpy.array, dataset of one variable
    y           : numpy.array, dataset of other variable
    p           : int, number of observation that is left out of the correlation analysis
    method      : The method to calculate correlation coefficients can be 'pearsonr', 'spearmanr', 'kendall', 'RMSD', or 'aRMSD'

    return the correlation given a dataset consists of paired observations where each (x_i, y_i) pair is related to each other
    """
    assert p<len(x), print("p should lower than number of observation")

    dat = pd.DataFrame([x, y], index=['X', 'Y']).T
    dat = dat.dropna()
    _x = np.array(dat.X)
    _y = np.array(dat.Y)

    bootstrap_correlations = []
    # Loop over data for leave-p-out cross-validation
    for i in range(len(_x) - p + 1):
        # Create dataset by leaving out p data points
        indices = np.delete(np.arange(len(_x)), np.s_[i:i+p])

        # Select corresponding elements from both x and y arrays
        select_x = _x[indices]
        select_y = _y[indices]

        # Calculate correlation coefficient
        corr, _ = _corr_coef(select_x, select_y, method)
        bootstrap_correlations.append(corr)

        # Analyze the distribution
        mean_corr = np.mean(bootstrap_correlations)
        std_corr = np.std(bootstrap_correlations)
        # confidence_interval = np.percentile(bootstrap_correlations, [2.5, 97.5])

    return mean_corr, std_corr


def corr_leave_p_out_matrix(data, keys, p=2, method='pearsonr'):
    """
    Parameters
    ----------
    data        : dataset contains the set of variables for correlation analysis
    p           : int, number of observation that is left out of the correlation analysis
    keys        : column names of dataframe to calculate correlation coefficients
    method      : The method to calculate correlation coefficients can be 'pearsonr', 'spearmanr', 'kendall', 'RMSD', or 'aRMSD'
    """
    table = pd.DataFrame(columns=keys, index=range(len(keys)))
    for i in range(1, len(keys)):
        for j in range(i):
            # x = pd.DataFrame.to_numpy(data[keys[i]])
            x = data[keys[i]]
            # y = pd.DataFrame.to_numpy(data[keys[j]])
            y = data[keys[j]]
            if len(x)>p:
                mean_corr, std_corr = corr_leave_p_out(x, y, p, method)
                text = r'n=' +str(len(x)) +'; corr=' +str('%5.3f' %mean_corr) +' ± ' +str('%5.3e' %std_corr)
            else:
                text = r'n=' +str(len(x))
            table.iloc[i][keys[j]] = text

    return table


def _pd_mean_std(df, name_pIC='pIC50', measure='mean'):
    """
    Given a dataframe of cellular IC50/hill slope values of multiple experiments, 
    return mean/std of pIC50 for each inhibitor.

    Parameters:
    ----------
    df          : input dataframe
    name_pIC    : name of column
    measure     : statistical measure, can be 'mean' or 'median'
    ----------
    """
    assert measure in ['mean', 'median'], print("Please check the statistical measure again.")
    
    ID = np.unique(df['ID'])
    mean = []
    std = []
    for _ID in ID:
        if measure == 'mean':
            mean.append(df[name_pIC][df.ID == _ID].mean())
        else:
            mean.append(df[name_pIC][df.ID == _ID].median())
        std.append(df[name_pIC][df.ID == _ID].std())
    
    return pd.DataFrame([ID, mean, std], index=['ID', name_pIC, name_pIC+'_std']).T


def correlation_table(pIC50, pIC90):
    pIC90 = pIC90.T
    column = pIC90.columns
    table = pIC50
    table.columns = column
    n = len(column)
    for i in range(0, n):
        for j in range(0, n):
            if i>j:
                table[column[i]][j] = pIC90[column[i]][j]
    return table.replace(np. nan,'',regex=True)


# def _df_biochem_pIC50_pIC90(df, name=''):

#     df_update = df.copy()
#     N = len(df)
#     df_update.insert(len(df_update.columns), name+'pIC50', len(df_update))
#     df_update.insert(len(df_update.columns), name+'pIC90', len(df_update))

#     for i in range(N):
#         dat = df_update.iloc[i]
#         _pIC50 = -np.log10(dat[name+'IC50']*1E-6)
#         hill = dat['hill']
#         if hill > 0:
#             _pIC90 = f_pIC90(_pIC50, hill)
#         else:
#             _pIC90 = float('nan')
#         df_update.at[i, name+'pIC50'] = _pIC50
#         df_update.at[i, name+'pIC90'] = _pIC90

#     return df_update


# def _cell_row_pIC50_pIC90(row, name=''):
#     if row[name+'IC50_Mod']=='=':
#         pIC50 = -np.log10(row[name+'IC50']*1E-6)
#     else:
#         pIC50 = float('nan')
#     if row[name+'IC90_Mod']=='=' and row[name+'IC90']>0:
#         pIC90 = -np.log10(row.IC90*1E-6)
#     elif pIC50>0 and (row['hill']>0 or row['hill']>0):
#         pIC90 = f_pIC90(pIC50, row['hill'])
#     elif pIC50>0 and (row['hill']>0 or row['hill']<0):
#         pIC90 = f_pIC90(pIC50, -row['hill'])
#     else:
#         pIC90 = float('nan')
#     return pIC50, pIC90


def _df_pIC50_pIC90(df, name=''):
    """
    Given a dataframe of IC50/hill slope values of multiple experiments, 
    return pIC50/pIC90 for all inhibitor.

    Parameters:
    ----------
    df          : input dataframe
    name        : name of experiment
    ----------
    """
    assert ('pIC50' in df.columns) or ('IC50_uM' in df.columns), print("At least one of the column is IC50 (uM) or pIC50.")

    df_update = df.copy()
    N = len(df)
    
    pIC50_list = []
    pIC90_list = []
    for i in range(N):
        _pIC50, _pIC90 = _pIC50_pIC90(df_update.iloc[i], name=name)
        pIC50_list.append(_pIC50)
        pIC90_list.append(_pIC90)

    if not name+'pIC50' in df_update.columns:
        df_update.insert(len(df_update.columns), name+'pIC50', pIC50_list)
    if not name+'pIC90' in df_update.columns:
        df_update.insert(len(df_update.columns), name+'pIC90', pIC90_list)

    df_pIC50 = _pd_mean_std_pIC(df_update, 'pIC50')
    df_pIC90 = _pd_mean_std_pIC(df_update, 'pIC90')
    df_final = pd.merge(df_pIC50, df_pIC90, on='ID', how='outer')
    
    return df_final


def _pIC50_pIC90(row, name=''):
    """
    Given a row of IC50/hill slope values of one experiment, return pIC50/pIC90.

    Parameters:
    ----------
    row         : one row from input dataframe
    name        : name of experiment
    ----------
    """
    colnames = row.to_frame().T.columns
    if name+'pIC50' in colnames:
        pIC50 = row[name+'pIC50']
    elif name+'IC50_uM' in colnames:
        pIC50 = -np.log10(row[name+'IC50_uM']*1E-6)
    else:
        pIC50 = float('nan')
        pIC90 = float('nan')
        return pIC50, pIC90

    if name+'hill' in colnames:
        if name+'IC90' in colnames and row[name+'IC90']>0:
            pIC90 = -np.log10(row[name+'IC90_nM']*1E-6)
        elif pIC50>0 and row['hill']!=0:
            pIC90 = f_pIC90(pIC50, row['hill'])
        else:
            pIC90 = float('nan')
    else:
        pIC90 = float('nan')
    return pIC50, pIC90