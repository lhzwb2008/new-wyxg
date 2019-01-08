FROM centos:6
 
USER root

COPY ./xampp-linux-x64-5.6.39-0-installer.run /root/

RUN chmod 755 ./root/xampp-linux-x64-5.6.39-0-installer.run \
&& ./root/xampp-linux-x64-5.6.39-0-installer.run

COPY . /opt/lampp/htdocs/code

# 构建时要做的事，一般是执行shell命令，例如用来安装必要软件，创建文件（夹），修改文件

RUN mkdir -p /home/root/music/mp3 && \
mkdir -p /home/root/music/lrc && \
mkdir -p /home/root/music/mid && \
mkdir -p /home/root/music/wav && \
mkdir -p /home/root/music/accmid && \
mkdir -p /home/root/music/accmp3 && \
mkdir -p /home/root/music/accwav && \
mkdir -p /home/root/music/mixwav && \
chmod -R a+w /home/root/music 

# 挂载数据卷,指定目录挂载到宿主机上面,为了能够保存（持久化）数据以及共享容器间的数据，为了实现数据共享，例如日志文件共享到宿主机或容器间共享数据.
VOLUME /home/root/music



RUN yum -y install net-tools \
&& yum -y install gcc gcc-c++ cmake autoconf make automake python-setuptools \
&& yum -y install curl-devel apr-devel apr-util-devel \
&& tar xzf /opt/lampp/htdocs/code/Python-2.6.6.tgz \
&& cd Python-2.6.6 \
&& ./configure --prefix=/usr/local/python2.6 \
&& ln -sf /usr/local/python2.6/bin/python2.6 /usr/bin/python2.6 \
&& make \ 
&& make install \
&& tar xvf /opt/lampp/htdocs/code/simplejson-3.16.0.tar.gz \
&& cd simplejson-3.16.0 \
&& python2.6 ./setup.py install \
&& tar xvf /opt/lampp/htdocs/code/python-pinyin-0.8.0.tar.gz \
&& cd python-pinyin-0.8.0 \
&& python2.6 ./setup.py install \
&& tar xvf /opt/lampp/htdocs/code/timidity.tar \
&& cd TiMidity++-2.14.0 \
&& ./configure --prefix=/usr/local \
&& make \
&& make install \
&& mkdir /usr/local/share/timidity \
&& echo 'soundfont "/opt/lampp/htdocs/code/fluid.sf2"' >/usr/local/share/timidity/timidity.cfg \
&& rpm -i /opt/lampp/htdocs/code/lame.rpm \
&& yum -y install sox \
&& cd /opt/lampp/htdocs/code/scripts/sing \
&& make testcallso \
&& cp libniao.so /usr/lib/ \
&& cp libniao.so /usr/local/lib/ \
&& /sbin/ldconfig -v  \
&& chmod a+x /opt/lampp/htdocs/code/scripts/sing/testcallso \
&& chmod a+x /opt/lampp/htdocs/code/scripts/run_h5.sh \
&& chmod a+x /opt/lampp/htdocs/code/scripts/get_mid.sh \
&& chmod -R 777 /home/root \
&& chmod a+x /opt/lampp/htdocs/code/start.sh


# 启动容器时进入的工作目录
WORKDIR /opt/lampp/htdocs/code

CMD ["/opt/lampp/htdocs/code/start.sh"]

