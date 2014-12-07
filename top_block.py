#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Tue Jan 17 04:01:56 2012
##################################################

from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import usrp2
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx

class top_block(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(self, title="Top Block")

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 32000

		##################################################
		# Blocks
		##################################################
		self.usrp2_sink_xxxx_0 = usrp2.sink_32fc()
		self.usrp2_sink_xxxx_0.set_interp(16)
		self.usrp2_sink_xxxx_0.set_center_freq(900e6)
		self.usrp2_sink_xxxx_0.set_gain(0)
		self.usrp2_sink_xxxx_0.config_mimo(usrp2.MC_WE_DONT_LOCK)
		self.gr_noise_source_x_0 = gr.noise_source_c(gr.GR_GAUSSIAN, 1, 42)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_noise_source_x_0, 0), (self.usrp2_sink_xxxx_0, 0))

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = top_block()
	tb.Run(True)

