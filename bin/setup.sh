#!/bin/bash
#Exit on error:
set -ex

# NOTE:
#To get this working on Debian, you need to install sudo first, add the current user to the sudoers
# group, and then you can run this - either that or you can manually run the sudo lines first
# in a root console

#Get the directory in which this file lives, de-referencing any symbolic links
#This works on OSX and Linux:
THIS_DIR="$(cd "$(dirname "$0")" && pwd -P)"

TMP_DIR="$HOME/tmp/snoutScanSetup/"

#Make sure we're in an uprgaded state:
sudo apt-get update -y
sudo apt-get upgrade -y

#Install dependencies here:
sudo apt-get install -y fortunes libsm6 libxrender1 libfontconfig1 libxext6

#Made with:
# conda env export --name snoutScan | xsel -b
snoutScanEnvDef='name: snoutScan
channels:
  - pytorch
  - menpo
  - defaults
dependencies:
  - blas=1.0=mkl
  - ca-certificates=2018.03.07=0
  - certifi=2018.4.16=py36_0
  - intel-openmp=2018.0.0=8
  - libedit=3.1=heed3624_0
  - libffi=3.2.1=hd88cf55_4
  - libgcc-ng=7.2.0=hdf63c60_3
  - libgfortran-ng=7.2.0=hdf63c60_3
  - libstdcxx-ng=7.2.0=hdf63c60_3
  - mkl=2018.0.2=1
  - mkl_fft=1.0.1=py36h3010b51_0
  - mkl_random=1.0.1=py36h629b387_0
  - ncurses=6.0=h9df7e31_2
  - numpy=1.14.3=py36hcd700cb_1
  - numpy-base=1.14.3=py36h9be14a7_1
  - openssl=1.0.2o=h20670df_0
  - pip=9.0.3=py36_0
  - python=3.6.5=hc3d631a_0
  - readline=7.0=ha6073c6_4
  - setuptools=39.0.1=py36_0
  - sqlite=3.23.1=he433501_0
  - tk=8.6.7=hc745277_3
  - wheel=0.31.0=py36_0
  - xz=5.2.3=h5e939de_4
  - zlib=1.2.11=ha838bed_2
  - faiss-cpu=1.2.1=py36_cuda0.0_2
  - pip:
    - alabaster==0.7.10
    - astroid==1.6.3
    - babel==2.5.3
    - backcall==0.1.0
    - bleach==2.1.3
    - chardet==3.0.4
    - click==6.7
    - cloudpickle==0.5.2
    - cycler==0.10.0
    - decorator==4.3.0
    - docutils==0.14
    - entrypoints==0.2.3
    - faiss==0.1
    - flask==0.12.2
    - flask-jwt==0.3.2
    - flask-sqlalchemy==2.3.2
    - future==0.16.0
    - gunicorn==19.7.1
    - html5lib==1.0.1
    - hyperopt==0.1
    - idna==2.6
    - imagesize==1.0.0
    - ipykernel==4.8.2
    - ipython==6.3.1
    - ipython-genutils==0.2.0
    - isort==4.3.4
    - itsdangerous==0.24
    - jedi==0.12.0
    - jinja2==2.10
    - jsonschema==2.6.0
    - jupyter-client==5.2.3
    - jupyter-core==4.4.0
    - kiwisolver==1.0.1
    - lazy-object-proxy==1.3.1
    - markupsafe==1.0
    - matplotlib==2.2.2
    - mccabe==0.6.1
    - mistune==0.8.3
    - namedlist==1.7
    - nbconvert==5.3.1
    - nbformat==4.4.0
    - networkx==1.11
    - nose==1.3.7
    - numpydoc==0.8.0
    - opencv-contrib-python==3.4.0.12
    - opencv-python==3.4.0.12
    - packaging==17.1
    - pandas==0.22.0
    - pandocfilters==1.4.2
    - parso==0.2.0
    - percache==0.3.0
    - pexpect==4.5.0
    - pickleshare==0.7.4
    - prompt-toolkit==1.0.15
    - psutil==5.4.5
    - ptyprocess==0.5.2
    - pybind11==2.2.3
    - pycodestyle==2.4.0
    - pyflakes==1.6.0
    - pygments==2.2.0
    - pyjwt==1.4.2
    - pylint==1.8.4
    - pymongo==3.6.1
    - pymysql==0.7.11
    - pyopengl==3.1.0
    - pyparsing==2.2.0
    - pyqt5==5.9.2
    - python-dateutil==2.7.2
    - pytz==2018.4
    - pyzmq==17.0.0
    - qtawesome==0.4.4
    - qtconsole==4.3.1
    - qtpy==1.4.1
    - requests==2.18.4
    - rope==0.10.7
    - scipy==1.1.0
    - simplegeneric==0.8.1
    - sip==4.19.8
    - six==1.11.0
    - snowballstemmer==1.2.1
    - sphinx==1.7.4
    - sphinxcontrib-websupport==1.0.1
    - spyder==3.2.8
    - sqlalchemy==1.2.7
    - testpath==0.3.1
    - tornado==5.0.2
    - traitlets==4.3.2
    - urllib3==1.22
    - wcwidth==0.1.7
    - webencodings==0.5.1
    - werkzeug==0.14.1
    - wrapt==1.10.11
prefix: /home/andromodon/.anaconda3/envs/snoutScan
'

#Make the /.condaUser symlink (previously /home/condaUser, but moved for osX compatability):
sudo ln -s "$HOME" /.condaUser || true
# 
# #Get our submodules:
# cd "$THIS_DIR"
# git submodule update --init

#Make the temp directory:
mkdir -p "$TMP_DIR"

cd "$TMP_DIR"

#Download miniconda:
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh

#Install miniconda3 (the -u lets it upgrade if it's already installed):
bash ./Miniconda3-latest-*.sh -b -u -p "$HOME"/.anaconda3

#Add the anacondaPath/bin to our bashrc:
echo -e '\n#Added by snoutScan setup.sh:\nexport PATH="$HOME/.anaconda3/bin:$PATH"' >> ~/.bashrc
#Source just the last line of .bashrc - the one we just added:
source <(tail -n 1 ~/.bashrc)

echo -e '\n#Added by snoutScan setup.sh:\nexport PATH="$PATH:'"$THIS_DIR"'/cli"' >> ~/.bashrc
#Source just the last line of .bashrc - the one we just added:
source <(tail -n 1 ~/.bashrc)

#dump our environments in the TMP_DIR:
echo "$snoutScanEnvDef" > ./snoutScanEnvDef.txt

#Set up conda snoutScan environment:
conda env create -f ./snoutScanEnvDef.txt

echo ''
echo 'Installation complete.'
