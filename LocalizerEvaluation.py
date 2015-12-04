#!/usr/bin/python
#! -*- encoding: utf-8 -*-

# this script is to evaluate the Incremental SfM pipeline to a known camera trajectory
# Notes:
#  - OpenMVG 0.8 is required

import commands
import os
import errno
import subprocess
import sys
import argparse
import json
import time

# Python version of Shell- 'mkdir -p'
def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

# Configure arguments parser
#

parser = argparse.ArgumentParser(description='Run OpenMVG localization on several datasets to evaluate the localization according to a ground truth.')

# OpenMVG SfM programs
parser.add_argument('-s', '--software', required=True, help='OpenMVG SfM software bin folder', metavar='SOFTWARE_PATH')
# input folder where datasets are stored
parser.add_argument('-i', '--input', required=True, help='Folder of the dataset', metavar='DATASETS_PATH')
# Results folder
parser.add_argument('-r', '--result', default='results', help='Directory to store the results', metavar='RESULT_PATH')
# Evaluation folder
parser.add_argument('-e', '--evaluation', default='evalutations', help='Directory to store evaluation files', metavar='EVALUATION_PATH')
# fake flag
parser.add_argument('-f', dest='fake_flag', action='store_true', help='Print the commands without executing them')
parser.set_defaults(fake_flag=False)

args = parser.parse_args()

OPENMVG_SFM_BIN = args.software
if not (os.path.exists(OPENMVG_SFM_BIN)):
  print("Invalid path : " + OPENMVG_SFM_BIN)
  sys.exit(1)

input_dir = args.input
dir_results_base = args.result
dir_eval_base = args.evaluation
fake_flag = args.fake_flag
if(fake_flag):
  print "Fake flag activated. Nothing will be executed."

# Run for each dataset of the input eval dir perform
#  . localization
#  . perform quality evaluation regarding ground truth camera trajectory

# we enter in a scene
for scene in os.listdir(input_dir):
  scene_full = os.path.join(input_dir, scene)

  # voctree + weights
  file_voctree = os.path.join(scene_full, "voctree.tree")
  file_weights = os.path.join(scene_full, "weights.weights")
  # structure for sift
  dir_matching_sift = os.path.join(scene_full, "structure/sift/matching")
  file_reconstruction_sift = os.path.join(scene_full, "structure/sift/reconstruction/sfm_data.json")
  # structure for cctag
  dir_matching_cctag = os.path.join(scene_full, "structure/cctag/matching")
  file_reconstruction_cctag = os.path.join(scene_full, "structure/cctag/reconstruction/sfm_data.json")

  # we enter in a movement
  for move in os.listdir(os.path.join(scene_full, 'moves')):
    move_full = os.path.join(scene_full, 'moves', move)

    # calibration file
    file_calibration = os.path.join(move_full, 'camera.cal')

    # ground truth
    dir_gt = os.path.join(move_full, 'gt')

    # result directory
    dir_results = os.path.join(dir_results_base, scene, move)
    mkdir_p(dir_results)

    # evaluation directory
    dir_eval = os.path.join(dir_eval_base, scene, move)
    mkdir_p(dir_eval)

    # for each image list we perform the tracking (SIFT or CCTAG or both, depending on option TODO)
    for image_list in os.listdir( os.path.join(move_full, 'lists') ):
      file_image_list = os.path.join(move_full, 'lists', image_list)

      # export file
      file_export_sift = os.path.join(dir_results, image_list + ".sift.abc")

      # statistics of evalQuality


      # final command for SIFT
      print('\n********************************************************************')
      print('scene  = ' + scene)
      print('move   = ' + move)
      print('images = ' + image_list)
      print('file_calibration          : ' + file_calibration          )
      print('file_voctree              : ' + file_voctree              )
      print('file_weights              : ' + file_weights              )
      print('dir_matching_sift         : ' + dir_matching_sift         )
      print('file_reconstruction_sift  : ' + file_reconstruction_sift  )
      print('dir_matching_cctag        : ' + dir_matching_cctag        )
      print('file_reconstruction_cctag : ' + file_reconstruction_cctag )
      print('dir_gt                    : ' + dir_gt                    )
      print('file_image_list           : ' + file_image_list           )
      print('file_export_sift          : ' + file_export_sift          )

      command = os.path.join(OPENMVG_SFM_BIN, "openMVG_main_voctreeLocalizer") + ' \\\n'
      command += " -c " + file_calibration + ' \\\n'
      command += " -t " + file_voctree + ' \\\n'
      command += " -w " + file_weights + ' \\\n'
      command += " -d " + file_reconstruction_sift + ' \\\n'
      command += " -s " + dir_matching_sift + ' \\\n'
      command += " -m " + file_image_list + ' \\\n'
      command += " -e " + file_export_sift

      print ('The following command will be executed :')
      print ( command )
      if(not fake_flag):
        proc = subprocess.Popen((str(command)), shell=True)
        proc.wait()


      # export file
      file_export_cctag = os.path.join(dir_results, image_list + ".cctag.abc")

      # final command for CCTAG
      command = os.path.join(OPENMVG_SFM_BIN, "openMVG_main_cctagLocalizer") + '\\\n'
      command += " -c " + file_calibration + ' \\\n'
      command += " -d " + file_reconstruction_cctag + ' \\\n'
      command += " -s " + dir_matching_cctag + ' \\\n'
      command += " -m " + file_image_list + ' \\\n'
      command += " -e " + file_export_cctag

      print ('The following command will be executed :')
      print ( command )
      if(not fake_flag):
        proc = subprocess.Popen((str(command)), shell=True)
        proc.wait()


      # ground truth evaluation
      print ('SIFT and CCTag localizations are done. The ground truth evaluation will now perform :')

      # for SIFT
      print ('Evaluation for SIFT localization:')
      command = os.path.join(OPENMVG_SFM_BIN, "openMVG_main_evalQuality") + '\\\n'
      command += " -i " + dir_gt + '\\\n'
      command += " -c " + file_export_sift + '\\\n'
      command += " -o " + os.path.join(dir_eval, image_list + "_sift")

      print ('The following command will be executed :')
      print ( command )
      if(not fake_flag):
        proc = subprocess.Popen((str(command)), shell=True)
        proc.wait()

      # for CCTAG
      print ('Evaluation for CCTAG localization:')
      command = os.path.join(OPENMVG_SFM_BIN, "openMVG_main_evalQuality") + '\\\n'
      command += " -i " + dir_gt + '\\\n'
      command += " -c " + file_export_cctag + '\\\n'
      command += " -o " + os.path.join(dir_eval, image_list + "_cctag")

      print ('The following command will be executed :')
      print ( command )
      if(not fake_flag):
        proc = subprocess.Popen((str(command)), shell=True, stdout=subprocess.PIPE)
        proc.wait()

sys.exit(0)
