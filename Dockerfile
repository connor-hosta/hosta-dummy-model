FROM nvidia/cuda:11.7.0-devel-ubuntu18.04

RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/7fa2af80.pub

RUN apt-get -y update && apt-get install -y --no-install-recommends \
         wget \
         python3-dev \
         nginx \
         ca-certificates \
         libglib2.0-0 \
         libgtk2.0-dev \
         python3-pip \
         build-essential \
         dos2unix \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install -U pip setuptools
RUN pip3 install shapely

RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install numpy==1.16.4 flask gevent==20.9.0 greenlet==0.4.17 gunicorn opencv-python==3.4.2.17 boto3 Pillow matplotlib ninja tensorboardX==2.2 PyYAML docopt scikit-image tqdm && \
        rm -rf /root/.cache

RUN pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113


# Set some environment variables. PYTHONUNBUFFERED keeps Python from buffering our standard
# output stream, which means that logs can be delivered to the user quickly. PYTHONDONTWRITEBYTECODE
# keeps Python from writing the .pyc files which are unnecessary in this case. We also update
# PATH so that the train and serve programs are found when the container is invoked.

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program/det2/detectron2/:${PATH}"
ENV MODEL_PATH="/opt/ml/model/models/"
# Set up the program in the image
COPY det2 /opt/program/det2

WORKDIR /opt/program/det2/detectron2
#RUN pip3 install -e detectron2
RUN python3 -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu113/torch1.10/index.html
RUN pip install opencv-python

RUN chmod 777 serve

RUN ln -s /usr/bin/python3 /usr/bin/python & \
    ln -s /usr/bin/pip3 /usr/bin/pip
# RUN dos2unix *
