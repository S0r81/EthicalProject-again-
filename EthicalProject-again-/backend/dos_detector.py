# Import required Ryu core components and OpenFlow v1.3
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4
from collections import defaultdict
import time
import os

# Define a custom Ryu app for detecting DoS attacks and responding with host migration
class DoSDetector(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]  # Use OpenFlow 1.3

    def __init__(self, *args, **kwargs):
        super(DoSDetector, self).__init__(*args, **kwargs)
        self.mac_to_port = {}  # Keeps MAC-to-port mapping per switch
        self.ip_packet_count = defaultdict(int)  # Counts packets per destination IP
        self.last_check = time.time()  # Timestamp of last check
        self.threshold = 5  # Threshold (packets/sec) to trigger DoS detection
        self.migrated = False  # Prevents multiple migrations

    # Install default flow to send unknown packets to controller
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        # Table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        # Install flow entry
        mod = parser.OFPFlowMod(datapath=datapath, priority=0, match=match, instructions=inst)
        datapath.send_msg(mod)

    # Handle incoming packets (PacketIn events)
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        # Parse the incoming packet
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # Count packets by destination IP if it's an IPv4 packet
        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)
        if ipv4_pkt:
            dst_ip = ipv4_pkt.dst
            self.ip_packet_count[dst_ip] += 1
            print(f"[DEBUG] Packet to {dst_ip}, count: {self.ip_packet_count[dst_ip]}")

        src = eth.src
        dst = eth.dst
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        # Learn the source MAC address on the current port
        self.mac_to_port[dpid][src] = in_port

        # Check for potential DoS attacks every second
        now = time.time()
        if now - self.last_check >= 1.0:
            for ip, count in self.ip_packet_count.items():
                if count > self.threshold and not self.migrated:
                    self.logger.warning(f"⚠️ POSSIBLE DoS attack on {ip} — {count} packets/sec")
                    self.migrate_host()
                    self.migrated = True
            self.ip_packet_count.clear()
            self.last_check = now

        # Forward the packet out to the correct port
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD  # Flood if destination unknown

        actions = [parser.OFPActionOutput(out_port)]
        data = None if msg.buffer_id != ofproto.OFP_NO_BUFFER else msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    # Function to migrate host h3 from s2 to s1
    def migrate_host(self):
        self.logger.info("🚀 Initiating automatic migration of h3...")

        cmds = [
            # Disable old link
            'py net.configLinkStatus(\\"h3\\", \\"s2\\", \\"down\\")',
            # Add new link to switch s1
            'py net.addLink(h3, s1)',
            # Bring up new interface with same IP and route
            'py h3.cmd(\\"ifconfig h3-eth1 10.0.0.3/8 up\\")',
            'py h3.cmd(\\"route add default dev h3-eth1\\")',
            # Delete old interface
            'py h3.cmd(\\"ip link delete h3-eth0\\")',
            # Detach old link from switch s2
            'py s2.detach(\\"s2-eth1\\")',
            'py net.delLink(next(link for link in net.links if \\"s2-eth1\\" in str(link)))',
            # Clear OpenFlow rules on both switches
            'py os.system(\\"/usr/bin/ovs-ofctl del-flows s1 -O OpenFlow13\\")',
            'py os.system(\\"/usr/bin/ovs-ofctl del-flows s2 -O OpenFlow13\\")'
        ]

        # Write commands to /tmp/mncmd for Mininet's CLI loop to execute
        for i, cmd in enumerate(cmds):
            redirect = '>' if i == 0 else '>>'
            os.system(f"mnexec -a $(pgrep -f 'bash.*mn') sh -c \"echo '{cmd}' {redirect} /tmp/mncmd\"")

        # Wait for commands to apply
        time.sleep(2)

        # Check if h3’s new interface is now linked to s1
        verify = os.popen("ovs-vsctl list-ports s1").read()
        if "s1-eth3" in verify:
            self.logger.info("✅ Host h3 migration verified: h3-eth1 is attached to s1.")
        else:
            self.logger.error("❌ Host h3 migration failed or incomplete.")
            self.logger.error(verify)
