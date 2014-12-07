#!/usr/bin/env python
#
# Copyright 2005, 2006 Free Software Foundation, Inc.
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

# OFDM transmitter that works on both USRP1 and USRP2, standard and UHD driver
# Revised: Veljko Pejovic (veljko@cs.ucsb.edu)

from gnuradio import gr, blks2
from gnuradio import uhd
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser

import time, struct, sys, os, math
import ofdm
import usrp_transmit_path
#sys.path.append('/usr/local/lib/python2.6/dist-packages/ofdmnew2')
#import ofdmnew2_swig

class my_top_block(gr.top_block):
	def __init__(self, options):
		gr.top_block.__init__(self)

		self.txpath = usrp_transmit_path.usrp_transmit_path(options)
		self.connect(self.txpath)


	def _print_verbage(self):
		print "Using TX d'board %s"    % (self.subdev.side_and_name(),)
		print "modulation:      %s"    % (self._modulator_class.__name__)
		print "interp:          %3d"   % (self._interp)
		print "Tx Frequency:    %s"    % (eng_notation.num_to_str(self._tx_freq))

        def string_pass(): 
                fd=open('string_pipe','r')
                string=fd.read()
                usrp_transmit_path.string_pass_l2(string) 
                  
def main():

	def send_pkt(payload='',carrier_map="FE7F",eof=False):
		return tb.txpath.send_pkt(payload, eof,carrier_map)

	parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
	expert_grp = parser.add_option_group("Expert")
	parser.add_option("-s", "--size", type="eng_float", default=1024, help="set packet size [default=%default]")
	parser.add_option("-M", "--megabytes", type="eng_float", default=1.0, help="set megabytes to transmit [default=%default]")
	parser.add_option("","--discontinuous", action="store_true", default=False, help="enable discontinuous mode")
	parser.add_option("","--from-file", default=None, help="use file for packet contents")

	usrp_transmit_path.add_options(parser, expert_grp)
	ofdm.ofdm_mod.add_options(parser, expert_grp)

	(options, args) = parser.parse_args ()

	if len(args) != 0:
		parser.print_help()
		sys.exit(1)

	if options.tx_freq is None:
		sys.stderr.write("You must specify -f FREQ or --freq FREQ\n")
		parser.print_help(sys.stderr)
		sys.exit(1)

	if options.from_file is not None:
		source_file = open(options.from_file, 'r')


	tb = my_top_block(options)

	r = gr.enable_realtime_scheduling()
	if r != gr.RT_OK:
		print "Warning: failed to enable realtime scheduling"

	tb.start()                       # start flow graph

	# generate and send packets
	# variables used in transmission
	nbytes = int(10e6 * options.megabytes)	# Total number of bytes to be sent.	
	n = 0
	pktno = 0
	pkt_size = int(options.size)		# Packet size
    #    udata ="Transmission is success" 		# string which is to be sent	# Added Line
    #    print "udata",udata							# Added Line
	source_file = open("/home/kranthi/tx1.txt",'r') # Source file location	# Added Line
    #    source_file = open(options.from_file,'r')  				# Added Line
	file_size = os.path.getsize("/home/kranthi/tx1.txt")
	print file_size
	no_packets = math.ceil(file_size/pkt_size)
	print no_packets
	preamble = 0
	while n < nbytes:
	    if (pktno < 20):
		data = "This is Garbage data"	      
	    else:
		data = source_file.read(pkt_size - 2)# data from the file		# Original Line
		if data == '':
		    break;
	    payload = struct.pack('!H', pktno & 0xffff) + struct.pack('!H', preamble & 0xffff) + data # Constructing a packet. Pack a string in to given format. http://docs.python.org/library/struct.html
	    send_pkt(payload)				     	     # Sending packet
	    n += len(payload)
	    sys.stderr.write('.')				     # error message
	    if options.discontinuous and pktno % 5 == 4:	     # if discontinuous mode is selected pass for 1 sec after every 4 byte transmission. 
		time.sleep(1)
	    pktno += 1
	send_pkt(eof=True)

	tb.wait()
	
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
