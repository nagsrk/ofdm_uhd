#!/usr/bin/env python

from gnuradio import gr, blks2
from gnuradio import usrp2,window,audio
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
#!/usr/bin/env python
from optparse import OptionParser
import string
import os
import time, struct,sys
import ofdm
import usrp_transmit_path
import ofdmnew2_swig
from  alsaaudio import *





class sound_data(gr.top_block):
  def __init__(self,pkt_size):
         gr.top_block.__init__(self)   
         sample_rate=48000
         vlen=(pkt_size-2)/4
         print "in sound init" 
         print "vlen=",vlen
         self.sound_src=audio.source (sample_rate,"hw:0,0")
         #self.conv=gr.float_to_uchar()
         #self.msgq = gr.msg_queue(100)
         self.stream_to_vec=gr.stream_to_vector(gr.sizeof_float,vlen)
         self.vec_sink=gr.vector_sink_f(vlen)
         #self.msg_sink=gr.message_sink(gr.sizeof_float,self.msgq,1)
         self.connect(self.sound_src,self.stream_to_vec,self.vec_sink)
 
def main():
  src_sound=sound_data()
  src_sound.start()
  for i in range(0,10):
     data=src_sound.vec_sink.data()
     print "data=",data
  src_sound.stop()
  src_sound.wait()  



if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		packet_file.close()
		pass