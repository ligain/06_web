FROM centos:7

ADD . /home/ip2w
WORKDIR /home/ip2w

RUN yum install rpm-build git -y

RUN git config user.name "ligain" \
    && git config user.email "khokhlov86@gmail.com"

RUN chmod +x buildrpm.sh && ./buildrpm.sh ip2w.spec

RUN cp /root/rpm/RPMS/noarch/ip2w-0.0.1-1.noarch.rpm .