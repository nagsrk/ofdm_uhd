#!/usr/bin/env python
#
# Copyright 2005,2006,2007 Free Software Foundation, Inc.
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

from gnuradio import gr, gru, blks2
from gnuradio import eng_notation
import copy
import sys
import ofdm

class receive_path(gr.hier_block2):
	def __init__(self, rx_callback, options):
		gr.hier_block2.__init__(self, "receive_path",
				gr.io_signature(1, 1, gr.sizeof_gr_complex), # Input signature
				gr.io_signature(0, 0, 0))                    # Output signature

		options = copy.copy(options)    # make a copy so we can destructively modify

		self._verbose            = options.verbose
		self._log         = options.log
		self._rx_callback   = rx_callback      # this callback is fired when there's a packet available

		self.ofdm_rx = ofdm.ofdm_demod(options, callback=self._rx_callback)

		self.connect(self, self.ofdm_rx)

		if self._verbose:
			self._print_verbage()

	def add_options(normal, expert):
		normal.add_option("-v", "--verbose", action="store_true", default=False)
		expert.add_option("-S", "--samples-per-symbol", type="int", default=2, help="set samples/symbol [default=%default]")
		expert.add_option("", "--log", action="store_true", default=False, help="Log all parts of flow graph to files (CAUTION: lots of data)")

	add_options = staticmethod(add_options)

	def _print_verbage(self):
		print "\nReceive Path:"
		#'''print "modulation:      %s"    % (self._demod_class.__name__)'''
		#print "samples/symbol:  %3d"   % (self._samples_per_symbol)
