#!/usr/bin/env python
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from optparse import OptionParser
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import usrp2
from gnuradio import window
import time
# from current dir
from multiprocessing import Process ,Value

def timer_func(mp,Freq):
     while(1):
	time.sleep(1)
	print "1 second of data recorded" 
	mp.terminate()
	f=open('fft_data.dat','a')
	f_tmp=open('fft_data','r')
	for l in f_tmp:
	  f.write(l)
	time.sleep(8)
	print "restarting the process"
	mp=Process(target=loop,args=(Freq,))
	mp.start()
	#print "changing frequency"
	##if   tb.rxpath.u.tune(self.subdev.which(), self.subdev, target_freq):
	#mp.terminate()
	#print "waiting for  the transmitter to stop"
	#print "transmitter stopped"
	##ok=tb.rxpath.u.set_center_freq(freq)
	##if  ok:
	#f_set=Freq.value
	#if(f_set==920*10**6):
	  #Freq.value=900*10**6
	#else:
	  #Freq.value=920*10**6
	#count.value=1
	#print "frequency changed to ",Freq.value
	#mp=Process(target=main_loop,args=(sound_obj,count,Freq))
        #mp.start()		    
	
	
class fft(gr.top_block):
      def __init__(self):
	 gr.top_block.__init__(self)
	 gain=0.7
	 target_freq=930e6
	 decim=16
	 interface=""
	 MAC_addr=""
	 fft_size=512
	 self.u = usrp2.source_32fc()
	 self.u.set_decim(128)
	 self.u.set_center_freq(930e6)
	 self.u.set_gain(0)
	 self.u.config_mimo(usrp2.MC_WE_DONT_LOCK)
	 self.s2v = gr.stream_to_vector(gr.sizeof_gr_complex*1, 512)
	 self.f_sink = gr.file_sink(gr.sizeof_gr_complex*512, "fft_data")
	 self.f_sink.set_unbuffered(False)
	 self.fft = gr.fft_vcc(512, True, (window.blackmanharris(512)), True)
 	 self.connect(self.u,self.s2v,self.fft,self.f_sink)

def loop(Freq):
      fft_save=fft()
      fft_save.u.set_center_freq(Freq)
      fft_save.start()
      #print "in main loop"
      #time.sleep(8)
      fft_save.wait()


	 
if __name__ == '__main__':
	try:
              
              #loop(fft_save)
              Freq=900e6
              mp=Process(target=loop,args=(Freq,))
              mp.start()
              ##time.sleep(8)
              ###print "after main loop"
              p=Process(target=timer_func,args=(mp,Freq))
              p.start()
             
              #p.join()
	except KeyboardInterrupt:
		
		pass	 
	 