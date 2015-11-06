#!/usr/bin/python
#! -*- encoding: utf-8 -*-

# this script is to evaluate the Incremental SfM pipeline to a known camera trajectory
# Notes:
#  - OpenMVG 0.8 is required
#
# Usage:
#  $ 
#
#

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
parser.add_argument('-s', '--software', required=True, help='OpenMVG SfM software folder ( like [...]/build/software/SfM)', metavar='SOFTWARE_PATH')
# input folder where datasets are stored
parser.add_argument('-i', '--input', required=True, help='Folder of the dataset)', metavar='DATASETS_PATH')
# # camera calibration
# parser.add_argument('-c', '--calibration', required=True, help='Camera calibration')
# # voctree
# parser.add_argument('-t', '--voctree', required=True, help='Vocabulary tree')
# # weights
# parser.add_argument('-w', '--weights', required=True, help='Vocabulary tree weights')
# # Output file
# parser.add_argument('-o', '--output', default='trackedcameras.abc', help='Ouput Alembic files containing estimated camera poses', metavar='RECONSTRUCTIONS_PATH')
# Result file
parser.add_argument('-r', '--result', default='results.json', help='File to store the results', metavar='RESULT_VAR')
# fake flag
parser.add_argument('-f', dest='fake_flag', action='store_true', help='Print the command and not execute')
parser.set_defaults(fake_flag=False)

args = parser.parse_args()

OPENMVG_SFM_BIN = args.software
if not (os.path.exists(OPENMVG_SFM_BIN)):
  print("/!\ Please update the OPENMVG_SFM_BIN to the openMVG_Build/software/SfM/ path.")
  print("Invalid path : " + OPENMVG_SFM_BIN)
  sys.exit(1)

input_dir = args.input
fake_flag = args.fake_flag
if(fake_flag):
  print "fake"
if(args.fake_flag):
  print "fake flag"
# camera_calib   = args.calibration
# voctree        = args.voctree
# weights         = args.weights
# output_file    = args.output

# Run for each dataset of the input eval dir perform
#  . localization
#  . perform quality evaluation regarding ground truth camera trajectory

# we enter in a scene
for scene in os.listdir(input_dir):
  scene_full = os.path.join(input_dir, scene)

  # calibration file
  file_calibration = os.path.join(scene_full, "camera.cal")
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

    # ground truth
    dir_gt = os.path.join(move_full, 'gt')

    # result directory
    dir_results = os.path.join('results', scene, move)
    mkdir_p(dir_results)

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



# result_folder = {}

# for image_list in os.listdir(input_dir):

#   print ("Localization")
#   command = os.path.join(OPENMVG_SFM_BIN, "openMVG_main_voctreeLocalizer")
#   command += " -c " + camera_calib
#   command += " -t " + voctree
#   command += " -w " + weights
#   command += " -d " + "structure/sift/reconstruction/sfm_data.json"
#   command += " -s " + "structure/sift/matching"
#   command += " -m " + os.path.join(input_dir,image_list)
#   command += " -e " + "results/" + image_list + ".sift.abc"

#   print ("Executing : " + command)
#   # proc = subprocess.Popen((str(command)), shell=True)
#   # proc.wait()

#   print ("Quality evaluation")
#   command = os.path.join(OPENMVG_SFM_BIN, "openMVG_main_evalQuality")
#   command = command + " -i " + "gt"
#   command = command + " -c " + "results/" + image_list + ".sift.abc"
#   command = command + " -o " + "stats/" + image_list + ".sift"
#   print(command)
#   proc = subprocess.Popen((str(command)), shell=True)
#   proc.wait()

# for directory in os.listdir(os.path.join(input_eval_dir, "medias")):

#   full_directory = os.path.join(input_eval_dir,"medias",directory)
#   print directory
#   print full_directory


#   print ("Localization")
#   command = OPENMVG_SFM_BIN + "/openMVG_main_voctreeLocalizer"
#   command += " -c " + camera_calib
#   command += " -t " + voctree
#   command += " -w " + weights
#   command += " -d " + os.path.join(input_eval_dir, "reconstruction","sfm_data.json")
#   command += " -s " + os.path.join(input_eval_dir, "matching")
#   command += " -m " + full_directory
#   print ("executing : " + command)
#   proc = subprocess.Popen((str(command)), shell=True, stdout=subprocess.PIPE)
#   cout, cerr = proc.communicate()
#   print cout
#   proc.wait()

#   result = {}
#   line = proc.stdout.readline()
#   while line != '':
#     if 'Baseline error statistics :' in line:
#       basestats = {}
#       line = proc.stdout.readline()
#       line = proc.stdout.readline()
#       for loop in range(0,4):
#         basestats[line.rstrip().split(':')[0].split(' ')[1]] = float(line.rstrip().split(':')[1])
#         line = proc.stdout.readline()
#       result['Baseline error statistics'] = basestats
#     if 'Angular error statistics :' in line:
#       basestats = {}
#       line = proc.stdout.readline()
#       line = proc.stdout.readline()
#       for loop in range(0,4):
#         basestats[line.rstrip().split(':')[0].split(' ')[1]] = float(line.rstrip().split(':')[1])
#         line = proc.stdout.readline()
#       result['Angular error statistics'] = basestats
#     line = proc.stdout.readline()

#   result['time'] = time_folder
#   result_folder[directory] = result

# with open(args.result, 'w') as savejson:
#     json.dump(result_folder, savejson, sort_keys=True, indent=4, separators=(',',':'))


sys.exit(0)
