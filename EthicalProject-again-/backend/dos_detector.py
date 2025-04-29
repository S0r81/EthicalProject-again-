from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4
from collections import defaultdict
import time
import os


class DoSDetector(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(DoSDetector, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.ip_packet_count = defaultdict(int)  # IP-based packet counter
        self.last_check = time.time()
        self.threshold = 100  # packets/sec threshold for DoS detection
        self.migrated = False  # to prevent multiple migrations

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        # Install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                           ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                              actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=0,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # Try to get IPv4 packet
        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)
        if ipv4_pkt:
            dst_ip = ipv4_pkt.dst
            self.ip_packet_count[dst_ip] += 1
            print(f"[DEBUG] Packet to {dst_ip}, count: {self.ip_packet_count[dst_ip]}")

        src = eth.src
        dst = eth.dst

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.mac_to_port[dpid][src] = in_port

        # Every second, check for DoS attack
        now = time.time()
        if now - self.last_check >= 1.0:
            for ip, count in self.ip_packet_count.items():
                if count > self.threshold and not self.migrated:
                    self.logger.warning(f"⚠️ POSSIBLE DoS attack on {ip} — {count} packets/sec")
                    self.migrate_host()
                    self.migrated = True
            self.ip_packet_count.clear()
            self.last_check = now

        # Just send the packet out (no permanent flows)
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    def migrate_host(self):
        self.logger.info("🚀 Initiating automatic migration of h3...")

        # 1. Bring down old link
        os.system("mnexec -a $(pgrep -f 'bash.*mn') sh -c \"echo 'py net.configLinkStatus(\\\"h3\\\", \\\"s2\\\", \\\"down\\\")' > /tmp/mncmd\"")

        # 2. Add new link
        os.system("mnexec -a $(pgrep -f 'bash.*mn') sh -c \"echo 'py net.addLink(h3, s1)' >> /tmp/mncmd\"")

    # 3. Bring up new interface
        os.system("mnexec -a $(pgrep -f 'bash.*mn') sh -c \"echo 'h3 ifconfig h3-eth1 up' >> /tmp/mncmd\"")

    # 4. Clear old flows
        os.system("mnexec -a $(pgrep -f 'bash.*mn') sh -c \"echo 'sh ovs-ofctl del-flows s1 -O OpenFlow13' >> /tmp/mncmd\"")
        os.system("mnexec -a $(pgrep -f 'bash.*mn') sh -c \"echo 'sh ovs-ofctl del-flows s2 -O OpenFlow13' >> /tmp/mncmd\"")

        self.logger.info("✅ Host h3 migration completed.")


