# EvaLoc
EvaLoc (for Evaluation of Localization) is a Python script which allow to evaluate precision of camera localization with OpenMVG.

## Usage

```
usage: LocalizerEvaluation.py [-h] -s SOFTWARE_PATH -i DATASETS_PATH [-r RESULT_VAR] [-e EVALUATION_PATH] [-f]

Run OpenMVG localization on several datasets to evaluate the localization according to a ground truth.

optional arguments:
  -h,                  --help                        show this help message and exit
  -s SOFTWARE_PATH,    --software SOFTWARE_PATH      OpenMVG SfM software bin folder
  -i DATASETS_PATH,    --input DATASETS_PATH         Path to the dataset
  -r RESULT_PATH,      --result RESULT_PATH          Directory to store the results
  -e EVALUATION_PATH,  --evaluation EVALUATION_PATH  Directoy to evaluation files
  -f                                                 Print the commands without executing them
```

For more convenience you can modify the script `launch_default.sh` in order to lauch the evaluation with a simple `./launch_default.sh`.

When evaluation is complete you can find two new folders:
- `results` (or whater you choose with `-r` option) : all the Alembic files of the localizations, ordered in folders according to the dataset, move and style.
- `evaluations` (or whatever you choose with `-e` option) : all the files generated by the quality evaluation, especially an HTML file with statistics of the evaluation. Also ordered by dataset, move and style.

## Files structure
This script takes as input a **dataset**.

A **dataset** contains **scenes**.

A **scene** has:
- vocabulary tree (+ weights)
- **structure**
- **moves**

A **structre** is a combination of **matching** (\*.feat & \*.desc files) and **reconstruction** generated by OpenMVG. Actually two kinds of structures are supported : SIFT and CCTag.

A **move** is a camera movement with known poses (ground truth), a calibration file and different **styles** of images.

A **style** is a variation of the image (the pose is not affected) like motion blur activated, depth of field, black and white, etc.

For naming convention here is a sample of dataset folder. The first scene *buildings* has two moves (*pano* and *drone*) and the second scene *room* have one move (*move01*). Each move have two styles : *classic* and *blur*.

### Naming
```
└── dataset
    ├── buildings
    |   ├── moves
    |   │   ├── pano
    |   │   │   ├── gt
    |   │   │   ├── lists
    |   │   │   └── medias
    |   │   │       ├── classic
    |   │   │       └── blur
    |   │   └── drone
    |   │       ├── gt
    |   │       ├── lists
    |   │       └── medias
    |   │           ├── classic
    |   │           └── blur
    |   └── structure
    |       ├── cctag
    |       │   ├── matching
    |       │   └── reconstruction
    |       └── sift
    |           ├── matching
    |           └── reconstruction
    └── room
        ├── moves
        │   └── move01
        │       ├── gt
        │       ├── lists
        │       └── medias
        │           ├── classic
        │           └── blur
        └── structure
            ├── cctag
            │   ├── matching
            │   └── reconstruction
            └── sift
                ├── matching
                └── reconstruction
```

### Image listing
In each **lists** folder there is text files named *classic.txt* and *blur.txt*, they all the images in relative paths. Example for *classic.txt* :
```
../medias/classic/IMG_001.jpg
../medias/classic/IMG_002.jpg
[...]
../medias/classic/IMG_320.jpg
```

### Ground truth
In the *gt* folder there should be text files with camera poses + intrinsics. The names does not matter but their alphabetical order should be the same that the movement order and they should finish with `.png.camera` or `.jpg.camera`. The simpliest way is to use the same name of the images and add `.camera` at the end. Each ground truth file contains :
```
f 0 dx
0 f dy
0 0 1
k l m
a b c
d e f
g h i
x y z
w h
```
where :
- f = focal
- dx,dy = coordinates of optical center on the image
- k,l,m = distortion factors
- a to i = rotation matrix
- x,y,z = coordinates of optical center in 3D space
- w,h = width and height of the image
