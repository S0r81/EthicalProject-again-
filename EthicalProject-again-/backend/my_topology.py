# File: backend/my_topology.py

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch, RemoteController
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class MyTopo(Topo):
    """
    Custom topology:
    - Two switches (s1, s2)
    - Three hosts (h1, h2, h3)
    - Links:
        - h1 <-> s1
        - h2 <-> s1
        - h3 <-> s2
        - s1 <-> s2
    """
    def build(self):
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')

        host1 = self.addHost('h1')
        host2 = self.addHost('h2')
        host3 = self.addHost('h3')

        self.addLink(host1, switch1)
        self.addLink(host2, switch1)
        self.addLink(host3, switch2)
        self.addLink(switch1, switch2)

def run():
    """Start the Mininet network with the custom topology."""
    topo = MyTopo()
    net = Mininet(topo=topo, controller=RemoteController, switch=OVSSwitch, link=TCLink)
    net.start()
    info("\n[Topology] Network started. Use 'pingall' or 'iperf' to test.\n")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
