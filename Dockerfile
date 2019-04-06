FROM ubuntu:16.04

RUN mkdir -p /usr/src/app 
WORKDIR /usr/src/app 

COPY sources.zh.list /etc/apt/sources.list

# Various Python and C/build deps
RUN apt-get update --fix-missing  && \
#apt-get upgrade -y --fix-missing && \ 
    apt-get install build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev  -y --fix-missing  && \
    apt-get install libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libjpeg-dev libeigen3-dev python3 python3-pip python-qt4 tzdata -y --fix-missing

#RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip && \
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple opencv-python Pillow flask flask_cors && \
    rm -f /etc/localtime && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# Install Open CV - Warning, this takes absolutely forever
RUN apt-get install wget unzip -y  && cd ~ && wget https://github.com/opencv/opencv/archive/3.4.0.zip -o opencv.zip  && unzip opencv.zip -d opencv  && \ 
    cd opencv && \
    cd ~ && wget https://github.com/opencv/opencv_contrib/archive/3.4.0.zip -o opencv_contrib.zip  && \
    unzip opencv_contrib.zip -d opencv_contrib && cd opencv_contrib && \
    git checkout 3.4 && \
    cd ~/opencv && mkdir -p build && cd build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \ 
    -D INSTALL_C_EXAMPLES=ON \ 
    -D INSTALL_PYTHON_EXAMPLES=ON \ 
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \ 
    -D BUILD_EXAMPLES=OFF .. && \
    make -j4 && \
    make install && \ 
    ldconfig

COPY requirements.txt /usr/src/app/
RUN pip3 install --no-cache-dir -r requirements.txt && git clone https://github.com/turlabs/NISwGSP 

COPY . /usr/src/app