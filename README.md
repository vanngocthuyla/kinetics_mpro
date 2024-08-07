# Introduction

This project focuses on the fitting of concentration-response curves (CRC) from biochemical assays of Coronavirus (CoV) main protease (MPro).

The entire procedure comprises two main steps:

-	Global Fitting: This step utilizes a subset of the data to estimate shared parameters across all datasets. The shared parameters include the binding affinities between the enzyme and the substrate.
-	CRC Fitting and pIC50 Estimation: The shared parameters estimated from the global fitting are used to estimate local parameters for each CRC.

We used Bayesian regression to fit the datasets. Knowledge about kinetic variables is used to assign the prior information to estimate the parameters. Otherwise, uninformative priors can be used instead.


## Global Fitting

The global fitting of SARS-CoV-2 MPro or MERS-CoV MPro can be found in /mpro/sars or /mpro/mers, respectively.

## CRC Fitting

Using information on shared parameters estimated from the global fitting, each CRC can be estimated, including the binding affinities between the enzyme and the inhibitor. An example can be found in /mpro/CRC.

## CRC Fitting and pIC50 estimation

The code will automatically generate samples until the number of converged samples is sufficient to estimate the pIC50. An example can be found in /mpro/CRC_pIC50.

# Set up the running environment

To run the Bayesian regression, we need some python packages. 

  * jax v0.4.13
  * jaxlib v0.4.13
  * numpyro v0.4.13
  * pickle-mixin >= v1.0.2
  * arviz >= 0.15.1
  * json5
  * pymbar


If higher versions of JAX, JAXlib, and numpyro are installed, we need to check whether x64 `jax.numpy` can be used by executing the following code without any errors:

    import jax
    jax.config.update("jax_enable_x64", True)

# Running test

Set your working directory:
    
    DIR='/home/python'

Install the packages and download the GitHub repository:
    
    git clone 'https://github.com/vanngocthuyla/kinetic_mpro.git'

Create a folder `test` to test the example:
    
    cd kinetic_mpro
    mkdir test
    cd test

Now we can try to fit one CRC:

    python $DIR/kinetic_mpro/scripts/run_CRC_fitting.py --name_inhibitor "ID_14973" --input_file $DIR/kinetic_mpro/CRC/input/Input.csv --prior_infor $DIR/kinetic_mpro/CRC/input/Prior.json --fit_E_S  --fit_E_I --initial_values $DIR/kinetic_mpro/CRC/input/map_sampling.pickle --out_dir $DIR/kinetic_mpro/test --multi_var  --set_lognormal_dE  --dE 0.10 --niters 1000 --nburn 200  --nchain 4 --outlier_removal

Or fitting CRC and estimating pIC50:

    mkdir test_pIC50
    cd test_pIC50
    python $DIR/kinetic_mpro/scripts/run_CRC_fitting_pIC50_estimating.py --name_inhibitor "ID_11138" --input_file $DIR/kinetic_mpro/CRC/input/Input.csv --prior_infor $DIR/kinetic_mpro/CRC/input/Prior.json --fit_E_S  --fit_E_I --initial_values $DIR/kinetic_mpro/CRC/input/map_sampling.pickle --out_dir $DIR/kinetic_mpro/test_pIC50 --multi_var  --set_lognormal_dE  --dE 0.10 --niters 1000 --nburn 200  --nchain 4 --outlier_removal --exclude_first_trace --converged_samples 500 --enzyme_conc_nM 100 --substrate_conc_nM 1350
