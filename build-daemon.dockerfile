FROM centos/systemd

ADD . /home/ip2w/

RUN yum install -y https://centos7.iuscommunity.org/ius-release.rpm \
    && yum update -y \
    && yum install -y python36u python36u-devel python36u-pip \
    && yum -y install gcc \
    && pip3.6 install uWSGI==2.0.17.1 \
    && yum clean all

EXPOSE 8080

RUN yum install -y /home/ip2w/*.rpm; systemctl enable ip2w

CMD [ "/sbin/init" ]
