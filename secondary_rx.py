#!/usr/bin/env python
#
# Copyright 2006, 2007 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr, blks2,digital
from gnuradio import uhd
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser

import struct, sys

# from current dir
import usrp_receive_path
import ofdm
	
class my_top_block(gr.top_block):
	def __init__(self, callback, options):
		gr.top_block.__init__(self)
		self.rxpath = usrp_receive_path.usrp_receive_path(callback, options) 
		self.connect(self.rxpath)

def main():
	global n_rcvd, n_right, shift, sync
	n_rcvd = 0
	n_right = 0
	shift = 0
	sync = 1
	no_packets = 50 
	global packet_file
	packet_file = open('/home/kranthi/rx.txt','w')
	
	def rx_callback(ok, payload):
		global n_rcvd, n_right, shift, parser, tb, sync
		(preamble,) = struct.unpack('!H', payload[2:4])
		if (preamble == 11111):
			n_rcvd += 1
			shift = 0 
			(pktno,) = struct.unpack('!H', payload[0:2])
			if pktno == 20:
			    (no_packets,) = struct.unpack('!H', payload[4:])
			    print no_packets
			    no_packets += 20
			elif pktno < 20:
			    print 
			elif (pktno > 70 and pktno < 150):
			    print
			elif pktno >= 150:
			      if sync == 1:
				    print "\nReceived Synchronization packet in 920M Frequency"
				    if ok:
					(freq,) = struct.unpack('!L', payload[4:])#int(payload[4:])
					tb.rxpath.u.u.set_center_freq(freq,0)
					print "and shifting to ",freq," Frequency"
					sync = 0
			else: 
			    packet_file.write(payload[4:])
			if ok:
			    n_right += 1
			print "ok: %r \t pktno: %d \t n_rcvd: %d \t n_right: %d" % (ok, pktno, n_rcvd, n_right)
		else:
		      shift += 1
		      if (shift >= 10):
			  freq = 920*10**6
			  sync = 1
			  print "Shifting to 920M frequency"
			  tb.rxpath.u.u.set_center_freq(freq,0)
	global parser
	parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
	expert_grp = parser.add_option_group("Expert")
	parser.add_option("", "--snr", type="eng_float", default=30, help="set the SNR of the channel in dB [default=%default]")

	usrp_receive_path.add_options(parser, expert_grp)
	ofdm.ofdm_demod.add_options(parser, expert_grp)

	(options, args) = parser.parse_args ()

	if len(args) != 0:
		parser.print_help(sys.stderr)
		sys.exit(1)

	if options.rx_freq is None:
		sys.stderr.write("You must specify -f FREQ or --freq FREQ\n")
		parser.print_help(sys.stderr)
		sys.exit(1)
		
	#print "Receiving Packets in", options.rx_freq, "Frequncy"
	global tb
	tb = my_top_block(rx_callback, options)
	r = gr.enable_realtime_scheduling()
	if r != gr.RT_OK:
		print "Warning: failed to enable realtime scheduling"

	tb.start()
	tb.wait()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		packet_file.close()
		pass
