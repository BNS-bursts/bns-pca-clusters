#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (C) 2018-2019 James Alexander Clark <james.clark@ligo.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
pmns_pcatomat.py

Script to do a PCA TF analysis for seedless clustering input
"""

from __future__ import division
import os,sys
import cPickle as pickle
import numpy as np

from matplotlib import pyplot as pl

#import pycbc.types

from pmns_utils import pmns_waveform as pwave
from pmns_utils import pmns_waveform_data as pdata
from pmns_utils import pmns_pca as ppca

from scipy import io as sio

from pycbc.types import TimeSeries
from pycbc.waveform import taper_timeseries



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Construct the full waveform catalogue and perform PCA

# XXX: Hardcoding
nTsamples=16384
low_frequency_cutoff=1000
fcenter=2710
#loo=True
loo=False

eos="all"
#mass="135135"
mass="all"
viscosity="lessvisc"


# XXX: should probably fix this at the module level..
if eos=="all": eos=None
if mass=="all": mass=None
if viscosity=="all": viscosity=None


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Initialise
#

#
# Create the list of dictionaries which comprises our catalogue
#
waveform_data = pdata.WaveData(eos=eos,viscosity=viscosity, mass=mass)

# XXX: get rid of the DD2new waveform
for wave in waveform_data.waves:
    if wave['eos'] == "dd2new": waveform_data.remove_wave(wave)

#
# Create PMNS PCA instance for the full catalogue
#
pmpca = ppca.pmnsPCA(waveform_data, low_frequency_cutoff=low_frequency_cutoff,
        fcenter=fcenter, nTsamples=nTsamples)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Compute the projection coefficients for each waveform
#
magnitude_betas = np.zeros(shape=(waveform_data.nwaves, waveform_data.nwaves))
timefreq_betas = np.zeros(shape=(waveform_data.nwaves, waveform_data.nwaves))

nmaprows=256
nmapcols=2048
timefreq_principal_components = np.zeros(shape=(waveform_data.nwaves, nmaprows,
    nmapcols))

#
# Dump time-domain waveforms
#
#injections = {}
injections = []
names=[]

for w, wave in enumerate(waveform_data.waves):

    print "Projecting %s, %s ,%s (%d of %d)"%(
        wave['eos'], wave['mass'], wave['viscosity'], w+1,
        waveform_data.nwaves)

    # --- Fourier Domain Analysis --- #
    # Get complex spectrum of this waveform
    waveform = pwave.Waveform(eos=wave['eos'], mass=wave['mass'],
                              viscosity=wave['viscosity'])
    waveform.reproject_waveform()

    name = wave['eos']+'_'+wave['mass']
    names.append(name)

    #injections[name] = (pwave.taper_start(waveform.hplus),
    #                    pwave.taper_start(waveform.hcross))
    injections.append((pwave.taper_start(waveform.hplus),
                        pwave.taper_start(waveform.hcross)))

    # Standardise
    waveform_FD, target_fpeak, _ = ppca.condition_spectrum(
        waveform.hplus.data, nsamples=nTsamples)

    # Normalise
    waveform_FD = ppca.unit_hrss(waveform_FD.data,
                                 delta=waveform_FD.delta_f, domain='frequency')

    # Take projection
    projection = pmpca.project_freqseries(waveform_FD)
    magnitude_betas[w, :]  = np.copy(projection['magnitude_betas'])

    # --- Wavelet Domain Analysis --- #

    # Make CWT TF map
    waveform_tfmap = ppca.build_cwt(waveform.hplus)
    height, width = waveform_tfmap['map'].shape

    # Project
    tf_projection = pmpca.project_tfmap(waveform_tfmap,
                                        this_fpeak=pmpca.fpeaks[w])

    timefreq_betas[w,:] = np.copy(tf_projection['timefreq_betas'])

    # Reshape to original dims
    for p in xrange(waveform_data.nwaves):
        timefreq_principal_components[p, :, :] = \
            pmpca.pca['timefreq_pca'].components_[p, :].reshape(height,
                                                                width)

timefreq_mean = pmpca.pca['timefreq_mean'].reshape(height, width)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Dump to mat files
#


#
# Extract and dump ALL relevant data (including PCs)
#
print pmpca.pca.keys()

outputdata = {
    'injection_waves':injections,
    'waveform_names':names,
    'fourier_frequencies':pmpca.sample_frequencies,
    'time_domain_waveforms':pmpca.cat_timedomain,
    'fcenter':2710.0,
    'fpeaks':pmpca.fpeaks,
    'fourier_magnitudes':pmpca.magnitude,
    'aligned_fourier_magnitudes':pmpca.magnitude_align,
    'magnitude_spectrum_mean':pmpca.pca['magnitude_pca'].mean_,
    'magnitude_principal_components':pmpca.pca['magnitude_pca'].components_,
    'magnitude_coeffficients':magnitude_betas,
    'timefreq_maps': pmpca.original_image_cat,
    'timefreq_scales': pmpca.map_scales,
    'aligned_timefreq_maps': pmpca.align_image_cat,
    'timefreq_mean':timefreq_mean,
    'timefreq_betas':timefreq_betas,
    'timefreq_principal_components':timefreq_principal_components,
    'timefreq_frequencies':pmpca.map_frequencies,
    'timefreq_times':pmpca.map_times
}

sio.savemat('postmergerpca.mat', outputdata)
#sio.savemat('postmergerinj.mat', injections)




