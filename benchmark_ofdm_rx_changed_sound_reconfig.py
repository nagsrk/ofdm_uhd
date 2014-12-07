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

from gnuradio import gr, blks2
from gnuradio import uhd
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser
from  alsaaudio import * 
import struct, sys
import time
import ofdm
# from current dir
import usrp_receive_path
from multiprocessing import Process ,Value,Queue



#def timer_func(count,mp,tb):
     #freq=920*10**6
     #while(1):
	#while(count.value==1):
	  #count.value=0
	  #time.sleep(2)
	#print "changing frequency"
	##if   tb.rxpath.u.tune(self.subdev.which(), self.subdev, target_freq):
	#mp.terminate()
	#print "terminated the receiver process"
	
	#ok=tb.rxpath.u.set_center_freq(freq)
	#if  ok:
			    #print "frequency changed to ",freq
			    #count.value=1
			    #tb.start()
			    #if(freq==920*10**6):
			      #freq=900*10**6
			    #else:
			      #freq=920*10**6
			    ##raise ValueError, eng_notation.num_to_str(options.rx)
	#else:
			    #count.value=1
			    #print "Failed to set Rx frequency to %d" % (freq)
def timer_func(count,mp,Freq,sound_obj):
     while(1):
	while(count.value==1):
	  count.value=0
	  time.sleep(8)
	print "changing frequency"
	#if   tb.rxpath.u.tune(self.subdev.which(), self.subdev, target_freq):
	mp.terminate()
	print "waiting for  the transmitter to stop"
	print "transmitter stopped"
	#ok=tb.rxpath.u.set_center_freq(freq)
	#if  ok:
	f_set=Freq.value
	if(f_set==920*10**6):
	  Freq.value=900*10**6
	else:
	  Freq.value=920*10**6
	count.value=1
	print "frequency changed to ",Freq.value
	mp=Process(target=main_loop,args=(sound_obj,count,Freq))
        mp.start()		    


class my_top_block(gr.top_block):
	def __init__(self, callback, options):
		gr.top_block.__init__(self)
	
		self.rxpath = usrp_receive_path.usrp_receive_path(callback, options) 
		self.connect(self.rxpath)
class sound_rcv(gr.top_block):
         def __init__(self):
	    gr.top_block.__init__(self)
            self.sample_rate=44100
	    self.sound_sink=PCM(type=PCM_PLAYBACK,mode=PCM_NORMAL,card='default')
	    self.sound_sink.setrate(self.sample_rate)
	    self.sound_sink.setperiodsize(32)
	    self.sound_sink.setformat(PCM_FORMAT_FLOAT_LE)
	    self.sound_sink.setchannels(1)
	    #self.vec_source=gr.file_source_f(self.data,0)
            #self.sound_sink=audio.sink (sample_rate,"hw:0,0")
            #self.connect(vec_source,sound_sink)
         
         def send_data(self,cdata):
              for i in range(0,len(cdata)): 
		self.data.append(cdata[i]) 
          


def main_loop(sound_obj,count,Freq):
  
	global n_rcvd, n_right ,data
	n_rcvd = 0
	n_right = 0
        data=""
        
	global packet_file
	packet_file = open('/usr/local/share/gnuradio/examples/audio/sound','a')
	def rx_callback(ok, payload):
		global n_rcvd, n_right
		global data
		count.value=1 #reset the counter
		n_rcvd += 1
		(pktno,) = struct.unpack('!H', payload[0:2])
		
		if ok:
		    n_right += 1
	        #if pktno > 19:
		  #print "writing to file\n"	
		
                 #if (len(data)<1024):  
                   #print "length of payload",len(payload)
                   #data=data+payload[2:]
                 #else:  
                    #data_buff=data[1024:]
                    print "length of data",len(payload[2:])   
                    sound_obj.sound_sink.write(payload[2:])
		    #data=data_buff
                
		print "ok: %r \t pktno: %d \t n_rcvd: %d \t n_right: %d" % (ok, pktno, n_rcvd, n_right)
	parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
	expert_grp = parser.add_option_group("Expert")
	parser.add_option("", "--snr", type="eng_float", default=30, help="set the SNR of the channel in dB [default=%default]")

	usrp_receive_path.add_options(parser, expert_grp)
	ofdm.ofdm_demod.add_options(parser, expert_grp)

	(options, args) = parser.parse_args ()

	if len(args) != 0:
		parser.print_help(sys.stderr)
		sys.exit(1)
        options.rx_freq=Freq.value
	if options.rx_freq is None:
		sys.stderr.write("You must specify -f FREQ or --freq FREQ\n")
		parser.print_help(sys.stderr)
		sys.exit(1)
		
       
	tb = my_top_block(rx_callback, options)
			      
	r = gr.enable_realtime_scheduling()
	if r != gr.RT_OK:
		print "Warning: failed to enable realtime scheduling"

	tb.start()                      # start flow graph
	tb.wait()                       # wait for it to finish
 

                    
                    
class  create_recv_control(object):
              def __init__(self, mp):
                self.mp = mp

              def get_recv_obj(self,tb,count):
		self.tb=tb
		self.count=count
		print "inside get_recv_obj"
              
              #def get_main_loop_handler(self,mp):
		#self.mp=mp
	      
	      def create_recv_controler(self): 
               p=Process(target=timer_func,args=(self.count,self.mp,self.tb))
               p.start()
              #p.join()

if __name__ == '__main__':
	try:
              sound_obj=sound_rcv()
              count=Value('i',1)
              Freq=Value('d',900*10**6)
              mp=Process(target=main_loop,args=(sound_obj,count,Freq))
              mp.start()
              print "after main loop"
              p=Process(target=timer_func,args=(count,mp,Freq,sound_obj))
              p.start()
              p.join()
                      
             
	except KeyboardInterrupt:
		packet_file.close()
		pass
