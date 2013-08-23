#!/usr/bin/env python
# -- coding: utf-8 --
#
############################################################################
#
# MODULE:	    ml.classify
#
# AUTHOR(S):   Pietro Zambelli (University of Trento)
#
# COPYRIGHT:	(C) 2013 by the GRASS Development Team
#
#		This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%Module
#%  description: Export machine learning results to a raster map
#%  keywords: imagery
#%  keywords: machine learning
#%  keywords: classification
#%  overwrite: yes
#%End
#%option G_OPT_I_GROUP
#%  key: group
#%  type: string
#%  description: Group name
#%  required: yes
#%end
#%option G_OPT_R_INPUTS
#%  key: rast
#%  description: Name of raster map(s) to include in group
#%  required: yes
#%end
#%option
#%  key: hdf
#%  type: string
#%  description: Name of the HDF file, where al the results and stats are saved
#%  required: yes
#%  answer: results.hdf
#%end
#%option
#%  key: seg_thresholds
#%  type: double
#%  multiple: yes
#%  description: Segment thresholds
#%  required: no
#%  answer: 0.01,0.02
#%end
#%option
#%  key: seg_opts
#%  type: string
#%  multiple: yes
#%  description: Segment options
#%  required: no
#%  answer: method=region_growing,similarity=euclidean,minsize=2
#%  guisection: Segment
#%end
#%option
#%  key: seg_name
#%  type: string
#%  description: Name for output raster maps from segment
#%  required: no
#%  answer: seg__%.2f
#%  guisection: Segment
#%end
#%option
#%  key: data
#%  type: string
#%  description: Name of the statistic data contained in the HDF file
#%  required: yes
#%  answer: K_all
#%end
#%option
#%  key: datasum
#%  type: string
#%  description: Name of the statistic data summarising the previous classification
#%  required: yes
#%  answer: K_all2
#%end
#%option
#%  key: training_json
#%  type: string
#%  description: Name of the JSON file with the name, cat, and a list of ids
#%  required: no
#%  guisection: Training
#%  answer: training.json
#%end
#%option
#%  key: training_kchk1
#%  type: string
#%  description: Name for the training values in the HDF
#%  required: no
#%  answer: K_chk
#%  guisection: Training
#%end
#%option
#%  key: training_kchk2
#%  type: string
#%  description: Name for the training values in the HDF
#%  required: no
#%  answer: K_chk
#%  guisection: Training
#%end
#%option
#%  key: training_ychk
#%  type: string
#%  description: Name for the training values in the HDF
#%  required: no
#%  answer:
#%  guisection: Training
#%end
#%option
#%  key: training_number
#%  type: integer
#%  description: Number of training sample to use per category, if 0 all will be use
#%  required: no
#%  answer: 0
#%  guisection: Training
#%end
#%option
#%  key: training_conf
#%  type: string
#%  description: Name for the training configure file
#%  required: no
#%  answer:
#%  guisection: Training
#%end
#%option
#%  key: training_mls
#%  type: string
#%  description: Name of the dictionary containing the instance of the Machine Learning
#%  required: no
#%  answer: MLS
#%  guisection: Training
#%end
#%option
#%  key: training_key
#%  type: string
#%  description: Name of the key of the instance to train and use for classification
#%  required: no
#%  guisection: Training
#%end
#%option
#%  key: training_hdf
#%  type: string
#%  description: Name for the training HDF file, if not set the HDF with results will be used
#%  required: no
#%  answer:
#%  guisection: Training
#%end
#%option G_OPT_R_OUTPUT
#%  key: output
#%  description: Name for the classify map
#%  required: yes
#%end
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import sys

try:
    import pandas as pnd
except ImportError, e:
    print("""This module require Pandas to run.

Please install pandas: http://pandas.pydata.org/

""")
    raise ImportError(e)


from grass.script import parser
from grass.pygrass.modules import Module
from grass.pygrass.gis import Mapset
#from grass.pygrass.functions import get_lib_path
#
#path = get_lib_path("ml.class", "libmlcls")
#if path is None:
#    raise ImportError("Not able to find the path to libmlcls directory.")
#
#sys.path.append(path)
#
#from mlstats import get_gmaps


def new_tab(hdf, table, newtable, keys):
    tab = pnd.read_hdf(hdf, table)
    for k in keys:
        tab[k] = pnd.read_hdf(hdf, k)
    import ipdb; ipdb.set_trace()
    tab.to_hdf(hdf, newtable)


def main(opts, flgs):
    """
ml.super group=rgb hdf=results.hdf \
seg_thresholds=0.02,0.05 \
seg_opts="method=region_growing,minsize=2" \
seg_name=seg__%.2f \
training_conf=mlconf.py \
training_mls=BEST \
training_hdf=training.hdf \
training_ychk=y_chk \
training_kchk1=K_chk \
training_kchk2=K_chk \
training_key=tree \
output=mytree
    ml.super(group=rgb, hdf=results.hdf, seg_thresholds=0.01,0.05,
                seg_opts="method=region_growing,minsize=2",
                seg_name=seg__%.2f, stat_name=stat_%s.csv,
                stat_ratio_cols=photo_r_mean,photo_g_mean,photo_b_mean,
                stat_results=K_all, flags='sr', overwrite=True)
    ml.classify(training_json=training.json,
                training_conf=mlconf.py, training_mls=BEST,
                training_hdf=$PHD/edinburgh/segSVM/segments-ml/data.hdf
                training_ychk=y_chk hdf=results.hdf)
    ml.toraster(segment=seg__0.05, hdf=results.hdf, mlname=tree, output=mltree)

classify(data=opts['datasum'], training_conf=abstconf, training_mls=opts['training_mls'], training_hdf=absthdf, training_kchk=opts['training_kchk2'], training_ychk=opts['training_ychk'], training_key=opts['training_key'], hdf=opts['hdf'])
torast(segment=opts['seg_name'] % opts['thrs'][-1], hdf=opts['hdf'], mlname=opts['training_key'], output=opts['output'])

ml.super group=rgb hdf=results.hdf seg_thresholds=0.02,0.05 seg_opts="method=region_growing,minsize=2" seg_name=seg__%.2f training_conf=mlconf.py training_mls=BEST training_hdf=training.hdf training_ychk=y_chk training_kchk1=K_chk training_kchk2=K_chk2 training_key=tree output=mytree --o


from grass.pygrass.modules.grid import GridModule

sup = GridModule(cmd='ml.super', group='rgb',
    hdf='results.hdf',
    seg_thresholds=[0.02,0.05],
    seg_opts="method=region_growing,minsize=2",
    seg_name='seg__%.2f', training_conf='mlconf.py',
    training_mls='BEST',
    training_hdf='training.hdf',
    training_ychk='y_chk',
    training_kchk1='K_chk',
    training_kchk2='K_chk2',
    training_key='tree',
    output='mytree',
    overwrite=True)

    """
    mps = Mapset()
    cwd = os.getcwd()
    abstconf = os.path.abspath(opts['training_conf'])
    absthdf = os.path.abspath(opts['training_hdf'])
    print(cwd, abstconf, absthdf)
    os.chdir(mps.path())
    igrp = Module('i.group')
    igrp(group=opts['group'], input=opts['rast'].split(','))
    segstats = Module('ml.segstats')
    segstats(group=opts['group'], hdf=opts['hdf'],
             seg_thresholds=opts['thrs'], seg_opts=opts['seg_opts'],
             seg_name=opts['seg_name'], stat_results=opts['data'],
             flags='sr', overwrite=True)
    #import ipdb; ipdb.set_trace()
    classify = Module('ml.classify')
    classify(data=opts['data'],
             training_conf=abstconf,
             training_mls=opts['training_mls'],
             training_hdf=absthdf,
             training_kchk=opts['training_kchk1'],
             training_ychk=opts['training_ychk'], hdf=opts['hdf'])
    #import ipdb; ipdb.set_trace()
#    conf = imp.load_source("conf", abstconf)
#    mls = getattr(conf, opts['training_mls'])
#    new_tab(opts['hdf'], opts['data'], opts['datasum'], mls.keys())
#    classify(data=opts['datasum'],
#             training_conf=abstconf,
#             training_mls=opts['training_mls'],
#             training_hdf=absthdf,
#             training_kchk=opts['training_kchk2'],
#             training_ychk=opts['training_ychk'],
#             training_key=opts['training_key'], hdf=opts['hdf'])
    torast = Module('ml.toraster')
    torast(segment=opts['seg_name'] % opts['thrs'][-1], hdf=opts['hdf'],
           mlname=opts['training_key'], output=opts['output'])
    os.chdir(cwd)


if __name__ == "__main__":
    options, flags = parser()
    options['thrs'] = [float(thr)
                       for thr in options['seg_thresholds'].split(',')]
    main(options, flags)
