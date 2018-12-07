echo 'nameserver 211.137.191.26' > /etc/resolv.conf
yum install -y http://mirror.centos.org/centos/7/extras/x86_64/Packages/centos-release-scl-rh-2-2.el7.centos.noarch.rpm
yum install -y rh-nodejs8
scl enable rh-nodejs8 bash
echo 'scl enable rh-nodejs8 bash' >> ~/.bash_profile
yum install -y http://dl.fedoraproject.org/pub/epel/7/x86_64/Packages/e/epel-release-7-11.noarch.rpm
yum install -y zeromq zeromq-devel
npm install -g node-gyp --unsafe-perm=true --allow-root
npm install -g zmq --unsafe-perm=true --allow-root
npm config set strict-ssl false
npm install -g appium --unsafe-perm=true --allow-root
