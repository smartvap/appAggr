yum install epel-release
yum -y install openvpn easy-rsa
cp -r /usr/share/easy-rsa/ /etc/openvpn/easy-rsa
cp /usr/share/doc/easy-rsa-3.0.3/vars.example /etc/openvpn/easy-rsa/vars
cd /etc/openvpn/easy-rsa/3.0.3
./easyrsa init-pki
./easyrsa build-ca nopass
./easyrsa gen-req server nopass
./easyrsa sign server server
./easyrsa gen-dh

# client certificate
cp -r /usr/share/easy-rsa /etc/openvpn/client
cd /etc/openvpn/client/easy-rsa/3.0.3
cp /usr/share/doc/easy-rsa-3.0.3/vars.example ./vars
./easyrsa init-pki
./easyrsa gen-req ayakj nopass
cd /etc/openvpn/easy-rsa/3.0.3/
./easyrsa import-req /etc/openvpn/client/easy-rsa/3.0.3/pki/reqs/ayakj.req ayakj
./easyrsa sign client ayakj

cd /etc/openvpn/server/
cp /etc/openvpn/easy-rsa/3.0.3/pki/dh.pem .
cp /etc/openvpn/easy-rsa/3.0.3/pki/ca.crt .
cp /etc/openvpn/easy-rsa/3.0.3/pki/issued/server.crt .
cp /etc/openvpn/easy-rsa/3.0.3/pki/private/server.key .

mkdir -p /etc/openvpn/client/ayakj
cd /etc/openvpn/client/ayakj
cp /etc/openvpn/easy-rsa/3.0.3/pki/ca.crt .
cp /etc/openvpn/easy-rsa/3.0.3/pki/issued/ayakj.crt .
cp /etc/openvpn/client/easy-rsa/3.0.3/pki/private/ayakj.key .


cat > /etc/openvpn/server.conf <<!
local 192.168.206.4                             # 服务器IP
port 33194                                      # 占用端口
proto tcp                                       # 使用udp协议
dev tun                                         # 使用tun模式,也可使用tap模式
ca /etc/openvpn/server/ca.crt                   # CA证书
cert /etc/openvpn/server/server.crt             # 服务器证书
key /etc/openvpn/server/server.key              # 服务器密钥
dh /etc/openvpn/server/dh.pem                   # 指定证书位置
ifconfig-pool-persist /etc/openvpn/ipp.txt      # 存放每个人使用的IP
server 17.166.221.0 255.255.255.0               # 客户端DHCP地址池
push "route 192.168.206.0 255.255.255.0"        # VPN访问网段
push "redirect-gateway def1 bypass-dhcp"        # 所有流量都走VPN
push "dhcp-option DNS 8.8.8.8"                  # DNS主
push "dhcp-option DNS 114.114.114.114"          # DNS备
client-to-client                                # 允许客户端之间互通
keepalive 20 120                                # 保持连接时间
comp-lzo                                        # 开启VPN压缩
#duplicate-cn                                   # 允许多人使用同一个证书连接VPN,不建议使用
user openvpn                                    # 运行用户
group openvpn                                   # 运行组
persist-key
persist-tun
status openvpn-status.log
log-append  openvpn.log
verb 1                                          # 日志级别0-9,等级越高记录越多
mute 20
!

systemctl start openvpn@server

# 配置iptables及转发
systemctl stop firewalld.service
systemctl disable firewalld.service
firewall-cmd --state
yum -y install iptables iptables-services
systemctl enable iptables.service
# 数据包匹配表为nat；添加PREROUTING策略，即入站地址转换；源地址为VPN私有地址；包从哪个网络接口发送出去；
iptables --table nat --delete POSTROUTING --source 17.166.221.0/24 --out-interface ens33 --jump MASQUERADE
iptables --table nat --append POSTROUTING --source 17.166.221.0/24 --out-interface ens33 --jump MASQUERADE
systemctl start iptables.service
iptables -L -n
iptables -t nat -L -n