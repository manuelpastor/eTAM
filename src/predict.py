#!/usr/bin/env python

# -*- coding: utf-8 -*-
#
#    Description    eTAM component for running a predictive model
#                   
#
#    Authors:       Manuel Pastor (manuel.pastor@upf.edu) 
#
#    (c) PhI 2013

import sys
import os
import getopt
import cPickle as pickle

from utils import splitSDF
from utils import lastVersion
from utils import writeError
from utils import removefile

def predict (endpoint, molecules, verID=-1, detail=False):
    """Top level prediction function

       molecules:  SDFile containing the collection of 2D structures to be predicted
       verID:      version of the model that will be used. Value -1 means the last one
       detail:     level of detail of the prediction. If True the structure of the
                   closest compond will be returned
    """
    
    # compute version (-1 means last) and point normalize and predict to the right version
    vpath = lastVersion (endpoint,verID)
    if not vpath:
        return (False,"No versions directory found")
    
    sys.path.append(vpath)
    from imodel import imodel
    
    model = imodel(vpath)

    
    i=0
    pred = []
    mol=''
    fout = None

    # open SDFfile and iterate for every molecule
    try:
        f = open (molecules,'r')
    except:
        return (False,"No molecule found in %s; SDFile format not recognized" % molecules)
    
    for line in f:
        if not fout or fout.closed:
            i += 1
            mol = 'm%0.10d.sdf' % i
            fout = open(mol, 'w')

        fout.write(line)
    
        if '$$$$' in line:
            fout.close()

            ## workflow for molecule i (mol) ###########
            success, molN  = model.normalize (mol)
            if not success:
                pred.append((False, molN))
                continue
        
            predN = model.predict (molN, detail)
            
            pred.append((True,predN))
            ############################################

            removefile(mol)

    return (True, pred)

def presentPrediction (pred):
    
    """Writes the result of the prediction into a log file and prints some of them in the screen
    """

    if pred[0]:
        for x in pred[1]:
            if x[0]:
                for y in x[1]:
                    if y[0]:
                        if y[1] is float:
                            print "%8.3f" % y[1],
                        else:
                            print y[1]
                    else:
                        print y
                print
            else:
                print x
    else:
        print pred


def presentPredictionWS (pred):
    
    results = []
    
    if pred[0]:
        #loop for compounds
        for x in pred[1]:
            val = ''
            msg = ''
            stat = 1
            if x[0]:
                y = x[1][0]
                if y[0]:
                    #val = float(y[1])
                    val = y[1]
                    stat = 0
                else:
                    msg = str(y[1])
            else:
                msg = str(x[1])
            results.append((val,stat,msg))
    else:
        stat = 1
        val = ''
        msg = str(pred[1])
        results.append((val,stat,msg))

    pkl = open('results.pkl', 'wb')
    pickle.dump(results, pkl)
    pkl.close()

def testimodel():
    try:
        from imodel import imodel
    except:
        return

    print 'please remove file imodel.py or imodel.pyc from eTAM/src'
    sys.exit(1)
    
def usage ():
    """Prints in the screen the command syntax and argument"""
    
    print 'predict -e endpoint [-f filename.sdf][-v 1|last]'

def main ():

    endpoint = None
    ver = -99
    auto = False
    mol = None

    try:
       opts, args = getopt.getopt(sys.argv[1:], 'ae:f:v:h')

    except getopt.GetoptError:
       writeError('Error. Arguments not recognized')
       usage()
       sys.exit(1)

    if args:
       writeError('Error. Arguments not recognized')
       usage()
       sys.exit(1)
        
    if len( opts ) > 0:
        for opt, arg in opts:

            if opt in '-e':
                endpoint = arg
            elif opt in '-f':
                mol = arg
            elif opt in '-v':
                if 'last' in arg:
                    ver = -1
                else:
                    try:
                        ver = int(arg)
                    except ValueError:
                        ver = -99
            elif opt in '-a':
                auto = True
                mol = './input_file.sdf'
                ver = -1
                # calls from web services might not have PYTHONPATH updated
                sys.path.append ('/opt/RDKit/')
                sys.path.append ('/opt/standardise/')
            elif opt in '-h':
                usage()
                sys.exit(0)

    if ver == -99:
        usage()
        sys.exit (1)

    if not mol:
        usage()
        sys.exit (1)
        
    if not endpoint:
        usage()
        sys.exit (1)

    # make sure imodel has not been copied to eTAM/src. If this were true, this version will
    # be used, instead of those on the versions folder producing hard to track errors and severe
    # misfunction
    testimodel()
    
    result=predict (endpoint,mol,ver)
    
    if auto:
        presentPredictionWS(result)
    else:
        presentPrediction  (result)

    sys.exit(0)
        
if __name__ == '__main__':
    
    main()
