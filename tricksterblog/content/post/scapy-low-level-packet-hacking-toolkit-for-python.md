+++
author = "rl1987"
title = "Scapy: low level packet hacking toolkit for Python"
date = "2022-05-10"
draft = true
tags = ["python", "security"]
+++

To make HTTP requests with Python we can use requests module. To send and receive things via TCP
connection we can use stream sockets. However, what if we want to go deeper than this? To parse
and generate network packets, we can use [`struct`](https://docs.python.org/3/library/struct.html)
module. Depending on how deep in protocol stack are we working we may need to send/receive the
wire format buffer through raw sockets. This can be fun in a way, but if this kind of code is 
being written for research purposes (e.g. to find and demonstrate vulnerabilities in networking software)
dealing with protocol wire formats and raw sockets will yield fairly low ROI on your efforts. 

[Scapy](https://scapy.net/) is a Python module and interactive program for low-level network 
programming that attempts to make it easier without abstracting away the technical details. 
This project is fairly prominent in cybersecurity space and used for things
like exploit development, data exfiltration, network recon, intrusion detection and 
analysing captured traffic. Scapy integrates with data visualisation and report generation
tooling for presenting the results of your research to bug bounty program or during
the meeting with customer or management. The foundational idea for Scapy is proposing a
Python-based domain specific language for easy and quick wire format management.

Scapy can be installed through PIP and in some cases through operating system package managers
(but make sure to check that version available through e.g. APT is not obsolete).

Once installed, we can run Scapy REPL by simply running `scapy`:

```
$ scapy
INFO: Can't import matplotlib. Won't be able to plot.
INFO: Can't import PyX. Won't be able to use psdump() or pdfdump().
WARNING: IPython not available. Using standard Python shell instead.
AutoCompletion, History are disabled.

                     aSPY//YASa
             apyyyyCY//////////YCa       |
            sY//////YSpcs  scpCY//Pp     | Welcome to Scapy
 ayp ayyyyyyySCP//Pp           syY//C    | Version 2.4.5
 AYAsAYYYYYYYY///Ps              cY//S   |
         pCCCCY//p          cSSps y//Y   | https://github.com/secdev/scapy
         SPPPP///a          pP///AC//Y   |
              A//A            cyP////C   | Have fun!
              p///Ac            sC///a   |
              P////YCpc           A//A   | What is dead may never die!
       scccccp///pSP///p          p//Y   |                     -- Python 2
      sY/////////y  caa           S//P   |
       cayCyayP//Ya              pY/Ya
        sY/PsY////YCc          aC//Yp
         sc  sccaCY//PCypaapyCP//YSs
                  spCPY//////YPSps
                       ccaacs

>>>
```

Simplest thing we can do with Scapy is reading a PCAP file. Let's download the following sample PCAP
from Wireshark project:

https://wiki.wireshark.org/uploads/1868d73fee89fce9d77c6ba21929e773/sip-rtp-opus-hybrid.pcap

We call `rdpcap()` function with PCAP file path to read it's contents:

```
>>> pkts = rdpcap("sip-rtp-opus-hybrid.pcap")
>>> pkts
<sip-rtp-opus-hybrid.pcap: TCP:0 UDP:7 ICMP:0 Other:0>
```

This reads all packets from PCAP file in one go. We may not want that if we have a large PCAP
file with a lot of packets captured. In that case, we would want to read packets iteratively - 
one at a time. This is possible through `PcapReader` object that can be instantiated from file
handle:

```
>>> in_f = open("sip-rtp-opus-hybrid.pcap", "rb")
>>> reader = PcapReader(in_f)
>>> reader
<scapy.utils.PcapReader at 0x1109daf40>
>>> for pkt in reader:
...:     print(pkt)
...: 
WARNING: Calling str(pkt) on Python 3 makes no sense!
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00E\x00\x01\xee\x1b\\@\x00@\x11\x05\x81\n\x00\x02\x14\n\x00\x02\x0f\x13\xc4\x13\xc4\x01\xda\x1a\x0eINVITE sip:test@10.0.2.15:5060 SIP/2.0\r\nVia: SIP/2.0/UDP 10.0.2.20:5060;branch=z9hG4bK-4237-1-0\r\nFrom: "opus/48000/2" <sip:sipp@10.0.2.20:5060>;tag=1\r\nTo: test <sip:test@10.0.2.15:5060>\r\nCall-ID: 1-4237@10.0.2.20\r\nCSeq: 1 INVITE\r\nContact: sip:sipp@10.0.2.20:5060\r\nMax-Forwards: 70\r\nContent-Type: application/sdp\r\nContent-Length:   128\r\n\r\nv=0\r\no=- 42 42 IN IP4 10.0.2.20\r\ns=-\r\nc=IN IP4 10.0.2.20\r\nt=0 0\r\nm=audio 6000 RTP/AVP 99\r\na=rtpmap:99 opus/48000/2\r\na=recvonly\r\n'
WARNING: Calling str(pkt) on Python 3 makes no sense!
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00E\x00\x04}\xb6\xdc\x00\x00@\x11\xa7q\n\x00\x02\x0f\n\x00\x02\x14\x13\xc4\x13\xc4\x04i\x1c\x9dSIP/2.0 200 OK\r\nVia: SIP/2.0/UDP 10.0.2.20:5060;branch=z9hG4bK-4237-1-0\r\nFrom: "opus/48000/2" <sip:sipp@10.0.2.20:5060>;tag=1\r\nTo: test <sip:test@10.0.2.15:5060>;tag=gm5D9rB47ggme\r\nCall-ID: 1-4237@10.0.2.20\r\nCSeq: 1 INVITE\r\nContact: <sip:test@10.0.2.15:5060;transport=udp>\r\nUser-Agent: FreeSWITCH-mod_sofia/1.6.12-20-b91a0a6~64bit\r\nAccept: application/sdp\r\nAllow: INVITE, ACK, BYE, CANCEL, OPTIONS, MESSAGE, INFO, UPDATE, REGISTER, REFER, NOTIFY, PUBLISH, SUBSCRIBE\r\nSupported: timer, path, replaces\r\nAllow-Events: talk, hold, conference, presence, as-feature-event, dialog, line-seize, call-info, sla, include-session-description, presence.winfo, message-summary, refer\r\nContent-Type: application/sdp\r\nContent-Disposition: session\r\nContent-Length: 283\r\nRemote-Party-ID: "test" <sip:test@10.0.2.15>;party=calling;privacy=off;screen=no\r\n\r\nv=0\r\no=FreeSWITCH 1480231472 1480231473 IN IP4 10.0.2.15\r\ns=FreeSWITCH\r\nc=IN IP4 10.0.2.15\r\nt=0 0\r\nm=audio 24196 RTP/AVP 99 101\r\na=rtpmap:99 opus/48000/2\r\na=fmtp:99 useinbandfec=1; minptime=10; maxptime=40\r\na=rtpmap:101 telephone-event/8000\r\na=fmtp:101 0-16\r\na=sendonly\r\na=ptime:20\r\n'
WARNING: more Calling str(pkt) on Python 3 makes no sense!
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00E\x00\x00z\xb6\xdf@\x00@\x11kq\n\x00\x02\x0f\n\x00\x02\x14^\x84\x17p\x00f\x18\x9a\x80\xe3]%\x00\x00\x03\xc0\x04>\xee\x04x\x00\xb2g\xa8\x1f@N\xf7x`\x9a@r2\xaf\x14\xdf!\x8c-\xb4U\xcek\xc6\\p[\xc2\xcf\x0b\x8e\xa9\x18\xb1.V\xe2l\xbe\x1c\x13\x1bR\xb7\x1dT\xf2\x80\x8cS\x98r!\xec\x13\xc4\xbd\x11l\x86\xd7\x80<\x8dO\x8e\xd3\xb6\x9e-6\xa2\x03;\xeb\xa3E\x06Ui'
b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00E\x00\x00\xbd\xb6\xf2@\x00@\x11k\x1b\n\x00\x02\x0f\n\x00\x02\x14^\x84\x17p\x00\xa9\x18\xdd\x80c]-\x00\x00!\xc0\x04>\xee\x04y\xe3`\xcf\xf3\x9d\xf3\xd0#M\xf0\x1d@\xe87L\x90\x06:\xfc\xc8\x7f\x8b~\x9f\x80\xe8\x961av2iw-\xca\xc1]'p.s\xaf\xbcRZb\x8e4\x9eJ\xe4E\xbf\xf9\xd7\xc7\xdcT\x03\x0f\x8c\x8b7\xb5\x0evpq\x15\xcf\xa1\xf9,\x92\x0c\xf9\xdf@\x0cB\x93v\xce\xa1\xa8\x06\x13\xbbo\xd8\xb7,\x9e\x05K79\xc6h\\\xda\x80\x86*\x9bn\xa2\xd8$\x85\xb3\xd3sE\xcb\xc8\xa1\xb2\x85p\x9c`\x9f\xa2\xfb\x96\xebF\r|\x1cG6\xa2\xa0\x82Tv\x160Pw\xd7o\xe2\rV;"
b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00E\x00\x00\xc2\xb7\x10@\x00@\x11j\xf8\n\x00\x02\x0f\n\x00\x02\x14^\x84\x17p\x00\xae\x18\xe2\x80c];\x00\x00V@\x04>\xee\x04zd\x97\xde\xaf-\xae\\\xd8\xe3\x94\x10\x05\xab1\t\x91\xec\xd82(\x8d\xe1\xa1\xcb\xa8os\xdf\xc6\x8c\xff\xd9\xdb\x94`\xd7\xb8\xc8L\x95.af\x0b\xde\xe9\xfa\xb4\xe4\xc5\x00\xd3d\x01\xe8\x19\xf2\xb6\xcbw\x17\xd1\xf4X\xe2\xdb\xc9\xad\xd2&\xd2\x1f\xaa\xaaJ\xe9\x84Y\x16\x0b\x0f\xf8\xfe4\x17\x12\x16\x84@\xe4d\xbe!rn\x14\x9f(\x89\xdd\xdf\xfbQ' .9H-\x94\x9b\xf0\x86\xdbK\xf1\xc4o=\xb6\xdc\xa5\xed\xe5\xb6\x86s){<\xfb\xf4\x8cv\x1a\x12\xf6\x00(\xf9n\xaf\x98lO%\x91Z\xa5\x9a-\x11n"
b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00E\x00\x00\xc2\xb9\x0f@\x00@\x11h\xf9\n\x00\x02\x0f\n\x00\x02\x14^\x84\x17p\x00\xae\x18\xe2\x80c]\xe3\x00\x02\xcc@\x04>\xee\x04{B\x08\xb7\xc2\x92l<\xa8s\xde- ,c\x07\xe1\x0b7\xa3\xc3\xd6\xc3\xce\x8dA\xce\xb6\xc9\x85\xb3Y\xbeQi\xff\x8f\xd0!\xf1'\xb6bV\xa2\x80\xb2\xe7\x8fbsW\xc3\x18f\xbf_u8z\xbc\xf8\xcapM\x08\xed\xa8.3\x13\x98\xb9v\xd23\xc7\x18\x8eY\x10\xfc\x1c\x98\xb1\xbfaj\xbf\x02\xdb\x7f\xc4j\x85c\xddz\x8d\xd6vk`\x15\x14\x98\xcc\x81\x89\x13\x104\x00:l\x96\xa3\xb6\xe5\xad\xd1#\xd8\x04i\x99\x03\xe60\xe1\x8f(\r\x90\x89{\x9f\xf3\x16\x9cw\xc1\x9e\xb8\xeb\xb4&eU\xdd6\xcd\xca\xec"
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00E\x00\x00\xc4\xba\x84@\x00@\x11g\x82\n\x00\x02\x0f\n\x00\x02\x14^\x84\x17p\x00\xb0\x18\xe4\x80c^`\x00\x04\xa1\x00\x04>\xee\x04{\xc2\x08\xcd\xab\x7f\x95\\"\xa8P@\xce\xa0\xf3\xe8\xa6_\x1fp\xb0G\xa9XgH\x180\xc2\xadzl\x8c\xd1q\x81\xf8\x9eY\x05lJ*s\xfc\x05\xacbC\xad\x8d?3?T\xa8lU26\xfd/\x9b\xc92\xc7\x93\xf1o/\x8c\xcbu\x1ew ~ed\xc75\xa2\xc5|\xba\xc4\x1a\x96\xecM6\x9e\xbb.\x1e\x0f\x85\xfbh\x04L\xf3\x91>\xa9\x19\x9d@\x08\xd9P\x1c>\x01\xf9\x12.\x7f%lH\x1c\x86\xd42\xdbq\x98\r\xc6_\xa0\x05\xe7\xe8Pz^K-\xfd8)F\x91\xda\x93{\xab\t3$\xe5\xa2\xbc\xbb'
>>> in_f.close()
```

As we can see, each packet is available in it's wire format. Scapy treats each packet as stack of layers.
Scapy layers correspond to network protocols and their wire formats.

Let us take the first packet and check if IP layer is available:

```
>>> first_pkt = pkts[0]
>>> first_pkt.haslayer(IP)
True
>>> IP in first_pkt
True
```

To parse packet from a specific layer, we can index it by the layer we want and let Scapy print all the fields:

```
>>> first_pkt[Ether]
<Ether  dst=00:00:00:00:00:00 src=00:00:00:00:00:00 type=IPv4 |<IP  version=4 ihl=5 tos=0x0 len=494 id=7004 flags=DF frag=0 ttl=64 proto=udp chksum=0x581 src=10.0.2.20 dst=10.0.2.15 |<UDP  sport=sip dport=sip len=474 chksum=0x1a0e |<Raw  load='INVITE sip:test@10.0.2.15:5060 SIP/2.0\r\nVia: SIP/2.0/UDP 10.0.2.20:5060;branch=z9hG4bK-4237-1-0\r\nFrom: "opus/48000/2" <sip:sipp@10.0.2.20:5060>;tag=1\r\nTo: test <sip:test@10.0.2.15:5060>\r\nCall-ID: 1-4237@10.0.2.20\r\nCSeq: 1 INVITE\r\nContact: sip:sipp@10.0.2.20:5060\r\nMax-Forwards: 70\r\nContent-Type: application/sdp\r\nContent-Length:   128\r\n\r\nv=0\r\no=- 42 42 IN IP4 10.0.2.20\r\ns=-\r\nc=IN IP4 10.0.2.20\r\nt=0 0\r\nm=audio 6000 RTP/AVP 99\r\na=rtpmap:99 opus/48000/2\r\na=recvonly\r\n' |>>>>
>>> first_pkt[UDP]
<UDP  sport=sip dport=sip len=474 chksum=0x1a0e |<Raw  load='INVITE sip:test@10.0.2.15:5060 SIP/2.0\r\nVia: SIP/2.0/UDP 10.0.2.20:5060;branch=z9hG4bK-4237-1-0\r\nFrom: "opus/48000/2" <sip:sipp@10.0.2.20:5060>;tag=1\r\nTo: test <sip:test@10.0.2.15:5060>\r\nCall-ID: 1-4237@10.0.2.20\r\nCSeq: 1 INVITE\r\nContact: sip:sipp@10.0.2.20:5060\r\nMax-Forwards: 70\r\nContent-Type: application/sdp\r\nContent-Length:   128\r\n\r\nv=0\r\no=- 42 42 IN IP4 10.0.2.20\r\ns=-\r\nc=IN IP4 10.0.2.20\r\nt=0 0\r\nm=audio 6000 RTP/AVP 99\r\na=rtpmap:99 opus/48000/2\r\na=recvonly\r\n' |>>
```

To print a packet in hexadecimal, we can use `hexdump()` function:

```
>>> hexdump(first_pkt)
0000  00 00 00 00 00 00 00 00 00 00 00 00 08 00 45 00  ..............E.
0010  01 EE 1B 5C 40 00 40 11 05 81 0A 00 02 14 0A 00  ...\@.@.........
0020  02 0F 13 C4 13 C4 01 DA 1A 0E 49 4E 56 49 54 45  ..........INVITE
0030  20 73 69 70 3A 74 65 73 74 40 31 30 2E 30 2E 32   sip:test@10.0.2
0040  2E 31 35 3A 35 30 36 30 20 53 49 50 2F 32 2E 30  .15:5060 SIP/2.0
0050  0D 0A 56 69 61 3A 20 53 49 50 2F 32 2E 30 2F 55  ..Via: SIP/2.0/U
0060  44 50 20 31 30 2E 30 2E 32 2E 32 30 3A 35 30 36  DP 10.0.2.20:506
0070  30 3B 62 72 61 6E 63 68 3D 7A 39 68 47 34 62 4B  0;branch=z9hG4bK
0080  2D 34 32 33 37 2D 31 2D 30 0D 0A 46 72 6F 6D 3A  -4237-1-0..From:
0090  20 22 6F 70 75 73 2F 34 38 30 30 30 2F 32 22 20   "opus/48000/2"
00a0  3C 73 69 70 3A 73 69 70 70 40 31 30 2E 30 2E 32  <sip:sipp@10.0.2
00b0  2E 32 30 3A 35 30 36 30 3E 3B 74 61 67 3D 31 0D  .20:5060>;tag=1.
00c0  0A 54 6F 3A 20 74 65 73 74 20 3C 73 69 70 3A 74  .To: test <sip:t
00d0  65 73 74 40 31 30 2E 30 2E 32 2E 31 35 3A 35 30  est@10.0.2.15:50
00e0  36 30 3E 0D 0A 43 61 6C 6C 2D 49 44 3A 20 31 2D  60>..Call-ID: 1-
00f0  34 32 33 37 40 31 30 2E 30 2E 32 2E 32 30 0D 0A  4237@10.0.2.20..
0100  43 53 65 71 3A 20 31 20 49 4E 56 49 54 45 0D 0A  CSeq: 1 INVITE..
0110  43 6F 6E 74 61 63 74 3A 20 73 69 70 3A 73 69 70  Contact: sip:sip
0120  70 40 31 30 2E 30 2E 32 2E 32 30 3A 35 30 36 30  p@10.0.2.20:5060
0130  0D 0A 4D 61 78 2D 46 6F 72 77 61 72 64 73 3A 20  ..Max-Forwards:
0140  37 30 0D 0A 43 6F 6E 74 65 6E 74 2D 54 79 70 65  70..Content-Type
0150  3A 20 61 70 70 6C 69 63 61 74 69 6F 6E 2F 73 64  : application/sd
0160  70 0D 0A 43 6F 6E 74 65 6E 74 2D 4C 65 6E 67 74  p..Content-Lengt
0170  68 3A 20 20 20 31 32 38 0D 0A 0D 0A 76 3D 30 0D  h:   128....v=0.
0180  0A 6F 3D 2D 20 34 32 20 34 32 20 49 4E 20 49 50  .o=- 42 42 IN IP
0190  34 20 31 30 2E 30 2E 32 2E 32 30 0D 0A 73 3D 2D  4 10.0.2.20..s=-
01a0  0D 0A 63 3D 49 4E 20 49 50 34 20 31 30 2E 30 2E  ..c=IN IP4 10.0.
01b0  32 2E 32 30 0D 0A 74 3D 30 20 30 0D 0A 6D 3D 61  2.20..t=0 0..m=a
01c0  75 64 69 6F 20 36 30 30 30 20 52 54 50 2F 41 56  udio 6000 RTP/AV
01d0  50 20 39 39 0D 0A 61 3D 72 74 70 6D 61 70 3A 39  P 99..a=rtpmap:9
01e0  39 20 6F 70 75 73 2F 34 38 30 30 30 2F 32 0D 0A  9 opus/48000/2..
01f0  61 3D 72 65 63 76 6F 6E 6C 79 0D 0A              a=recvonly..
```

To fully parse and pretty-print a packet we can call `show()` method on it:

```
>>> first_pkt.show()
###[ Ethernet ]###
  dst= 00:00:00:00:00:00
  src= 00:00:00:00:00:00
  type= IPv4
###[ IP ]###
     version= 4
     ihl= 5
     tos= 0x0
     len= 494
     id= 7004
     flags= DF
     frag= 0
     ttl= 64
     proto= udp
     chksum= 0x581
     src= 10.0.2.20
     dst= 10.0.2.15
     \options\
###[ UDP ]###
        sport= sip
        dport= sip
        len= 474
        chksum= 0x1a0e
###[ Raw ]###
           load= 'INVITE sip:test@10.0.2.15:5060 SIP/2.0\r\nVia: SIP/2.0/UDP 10.0.2.20:5060;branch=z9hG4bK-4237-1-0\r\nFrom: "opus/48000/2" <sip:sipp@10.0.2.20:5060>;tag=1\r\nTo: test <sip:test@10.0.2.15:5060>\r\nCall-ID: 1-4237@10.0.2.20\r\nCSeq: 1 INVITE\r\nContact: sip:sipp@10.0.2.20:5060\r\nMax-Forwards: 70\r\nContent-Type: application/sdp\r\nContent-Length:   128\r\n\r\nv=0\r\no=- 42 42 IN IP4 10.0.2.20\r\ns=-\r\nc=IN IP4 10.0.2.20\r\nt=0 0\r\nm=audio 6000 RTP/AVP 99\r\na=rtpmap:99 opus/48000/2\r\na=recvonly\r\n'

```

The SIP payload was not parsed. That's because Scapy mostly deals with binary protocols in
lower parts of network stack, which SIP is not. However, there are third party helper modules
to parse some of the application layer protocols, such as HTTP.

So we can read PCAP files with pre-captured packets, but what if we want to do some packet sniffing?
Assuming we have our system ready to use network interface in promiscuous mode, we can can call
`sniff()` function to get some packets from the network interface:

```
>>> for pkt in sniff(count=5):
...:     pkt.show()
...:
```

We can also use the very same BPF syntax for filtering sniffed packets that Wireshark, tcpdump
and many other tools support:

```
>>> for pkt in sniff(filter="udp", count=5):
...:     pkt.show()
...: 
```

To save captured packets into PCAP file for further analysis, we can use `wrpcap()` function:

```
>>> capture = sniff(filter="udp", count=5)
>>> capture
<Sniffed: TCP:0 UDP:5 ICMP:0 Other:0>
>>> wrpcap("udp.pcap", capture)
```

Now we can sniff (capture and parse) the network packets, but Scapy also supports packet generation for
doing all kinds of active trickery: network scanning, server probing, attacking systems by sending
malformed requests and so on.

Let us try pinging a server. To send ICMP packet to a specific we need to make IP datagram
with ICMP payload:

```
>>> pkt = IP(dst="8.8.8.8") / ICMP()
>>> pkt.show()
###[ IP ]### 
  version= 4
  ihl= None
  tos= 0x0
  len= None
  id= 1
  flags= 
  frag= 0
  ttl= 64
  proto= icmp
  chksum= None
  src= 192.168.16.130
  dst= 8.8.8.8
  \options\
###[ ICMP ]### 
     type= echo-request
     code= 0
     chksum= None
     id= 0x0
     seq= 0x0
```

Calling `sr1()` sends our packet on layer 3 and waits for single answer:

```
>>> sr1(pkt)
Begin emission:
Finished sending 1 packets.
...*
Received 4 packets, got 1 answers, remaining 0 packets
<IP  version=4 ihl=5 tos=0x0 len=28 id=0 flags= frag=0 ttl=118 proto=icmp chksum=0x63a7 src=8.8.8.8 dst=192.168.16.130 |<ICMP  type=echo-reply code=0 chksum=0xffff id=0x0 seq=0x0 |<Padding  load='\x00\x00\x00\x000000000000\x00\x00\x00\x00' |>>>
```

We got a proper ICMP reply, which means server is up.

For sending multiple packets and receiving responses (e.g. to implement a ping sweep) we
could use `sr()` function. To send multiple packets, but wait for single response
we can use `sr1_flood()` function. For more on this, see:

https://scapy.readthedocs.io/en/latest/api/scapy.sendrecv.html?highlight=sr1#module-scapy.sendrecv

Scapy overrides the `/` operator to implement layer stacking. It does not enforce the ordering
of layers to make sure it occurs in the same order as it should. Thus we can create some
pretty crazy packets:

```
>>> broken_pkt = ICMP() / UDP() / IP() / IP()
>>> broken_pkt
<ICMP  |<UDP  |<IP  frag=0 proto=ipencap |<IP  |>>>>
>>> broken_pkt.show()
###[ ICMP ]###
  type= echo-request
  code= 0
  chksum= None
  id= 0x0
  seq= 0x0
###[ UDP ]###
     sport= domain
     dport= domain
     len= None
     chksum= None
###[ IP ]###
        version= 4
        ihl= None
        tos= 0x0
        len= None
        id= 1
        flags=
        frag= 0
        ttl= 64
        proto= ipencap
        chksum= None
        src= 127.0.0.1
        dst= 127.0.0.1
        \options\
###[ IP ]###
           version= 4
           ihl= None
           tos= 0x0
           len= None
           id= 1
           flags=
           frag= 0
           ttl= 64
           proto= ip
           chksum= None
           src= 127.0.0.1
           dst= 127.0.0.1
           \options\

>>> hexdump(broken_pkt)
WARNING: No IP underlayer to compute checksum. Leaving null.
0000  08 00 F7 65 00 00 00 00 00 35 00 35 00 30 00 00  ...e.....5.5.0..
0010  45 00 00 28 00 01 00 00 40 04 7C CF 7F 00 00 01  E..(....@.|.....
0020  7F 00 00 01 45 00 00 14 00 01 00 00 40 00 7C E7  ....E.......@.|.
0030  7F 00 00 01 7F 00 00 01                          ........
```

This is by design, as we may want to generate arbitrarily broken packets
for the purposes of vulnerability research or exploitation. However we also
have to take care and make sure that layers are ordered properly when
normal packets are being created.

For more Scapy usage examples, see: https://scapy.readthedocs.io/en/latest/usage.html

What if you don't want to use Scapy REPL exclusively, but would prefer to
develop Python scripts or Jupyter notebooks? Everything that Scapy REPL
provides can be used in a regular Python environment if you put the following
import statement on the top:

```python
from scapy.all import *
```

Scapy has been used to unit-test network protocol implementations in Linux, OpenBSD
and RIOT projects. It has also been used to implement various offensive security
tools:

* [trackerjacker](https://github.com/calebmadrigal/trackerjacker) - WiFi network mapper.
* [wifiphisher](https://github.com/wifiphisher/wifiphisher) - rogue access point creation tool.
* [sshame](https://github.com/HynekPetrak/sshame) - SSH public key brute forcer.
* [ISF](https://github.com/dark-lbp/isf) - exploitation framework for attacking industrial systems.

For an example of Scapy being used for bug bounty PoC, take a look at HackerOne
report [411519](https://hackerone.com/reports/411519).
