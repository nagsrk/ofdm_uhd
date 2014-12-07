#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gnuradio import gr, blks2
from gnuradio import uhd,window,audio,digital
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import string
import os
import time, struct,sys
import ofdm
import usrp_transmit_path
# sys.path.append('/home/kranthi/gnuradio-3.6.0/gr-digital')			# Added Line
# sys.path.append('/usr/lib/python2.7/multiprocessing')			# Added Line
#import ofdmnew2_swig
from multiprocessing import Process,Value

class transmit(gr.top_block):
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
                
def transmitter_control(mp,Freq,norestart):
    while(1):
	sys.stderr.write('\nIn transmitter_control:\n')
	while(norestart.value==1):
		time.sleep(2)
	norestart.value=1       
	mp.terminate()
	f_set=Freq.value
	if(f_set==920*10**6):
	    Freq.value=900*10**6
	else:
	    Freq.value=920*10**6
	#sys.stderr.write('changing frequency')    
	print "Frequency changed to", Freq.value
	#print "main program terminated"			# Added Line
	mp=Process(target=Start_transmitter,args=(Freq,norestart))
	mp.start()                  
        		   
class trans_init():
    def __init__(self,Freq): 
        global parser
        parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
	expert_grp = parser.add_option_group("Expert")
	parser.add_option("-s", "--size", type="eng_float", default=1024, help="set packet size [default=%default]")
	parser.add_option("-M", "--megabytes", type="eng_float", default=10.0, help="set megabytes to transmit [default=%default]")
	parser.add_option("","--discontinuous", action="store_true", default=False, help="enable discontinuous mode")
	parser.add_option("","--from-file", default=None, help="use file for packet contents")
        parser.add_option("-e", "--interface", type="string", default="eth0", help="Select ethernet interface. Default is eth0")
	parser.add_option("-m", "--MAC_addr", type="string", default="", help="Select USRP2 by its MAC address.Default is auto-select")
	parser.add_option("-j", "--start", type="eng_float", default=1e7, help="Start ferquency [default = %default]")
	parser.add_option("-k", "--stop", type="eng_float", default=1e8,help="Stop ferquency [default = %default]")
	parser.add_option("", "--tune-delay", type="eng_float", default=1e-3, metavar="SECS", help="time to delay (in seconds) after changing frequency[default=%default]")
	parser.add_option("", "--dwell-delay", type="eng_float",default=1e-3, metavar="SECS", help="time to dwell (in seconds) at a given frequncy[default=%default]")
	parser.add_option("-G", "--gain", type="eng_float", default=None,help="set gain in dB (default is midpoint)")
	parser.add_option("-s", "--fft-size", type="int", default=256, help="specify number of FFT bins [default=%default]")# changed default value(256)
	parser.add_option("-d", "--decim", type="intx", default=16, help="set decimation to DECIM [default=%default]")	# changed default value(16)
        parser.add_option("-i", "--input_file", default="", help="radio input file",metavar="FILE")
        parser.add_option("-S", "--sense-bins", type="int", default=128, help="set number of bins in the OFDM block [default=%default]")
	
	usrp_transmit_path.add_options(parser, expert_grp)
	ofdm.ofdm_mod.add_options(parser, expert_grp)
	(self.options, self.args) = parser.parse_args ()
	#fd= os.open('/home/spann/Dropbox/spec_sense/fifo',os.O_RDONLY) # Open the named pipe to pass on the sensed info to the transmitter part
	if len(self.args) != 0:
		parser.print_help()
		sys.exit(1)
	if self.options.tx_freq is None:
		sys.stderr.write("You must specify -f FREQ or --freq FREQ\n")
		parser.print_help(sys.stderr)
		sys.exit(1)
	self.options.tx_freq=Freq.value
	#Freq.value=int(self.options.tx_freq)
	#print "freq=",self.options.tx_freq
	#print "trying to open the source file",self.options.input_file
	#if self.options.input_file is not "":
		#print "reading from file:",self.options.input_file 
		#global source_file
		#source_file = open(self.options.input_file, 'r')
	self.tb = transmit(self.options)
	r = gr.enable_realtime_scheduling()
	if r != gr.RT_OK:
		print "Warning: failed to enable realtime scheduling"
    
    def Data(self):    
            return self.options.megabytes 
        
    def return_obj(self):
           return self.tb     
    
    def return_options(self):
           return self.options
        
###################################################################################################################################################################
                                                              #SENSING CODE 
###################################################################################################################################################################
                                                                                                           
class tune(gr.feval_dd):
    def __init__(self, tb):
	gr.feval_dd.__init__(self)
	self.tb = tb
	
    def eval(self, ignore):
	try:
	    new_freq = self.tb.set_next_freq()
	    return new_freq
	except Exception, e:
	    print "tune: Exception: ", e
	    
class parse_msg(object):
    def __init__(self, msg):
	self.center_freq = msg.arg1()
	self.vlen = int(msg.arg2())
	assert(msg.length() == self.vlen * gr.sizeof_float)
	t = msg.to_string()
	self.raw_data = t
	self.data = struct.unpack('%df' % (self.vlen,), t)

class sensor(gr.top_block):
    def __init__(self,options,Freq):
	gr.top_block.__init__(self)
	if options.input_file == "":
	    self.IS_USRP2 = True
	else:
	    self.IS_USRP2 = False
	#self.min_freq = options.start
	#self.max_freq = options.stop
	self.min_freq = Freq.value-(3*10**6) # same as that of the transmitter bandwidth ie 6MHZ approx for a given value of decimation line option any more
	self.max_freq = Freq.value+(3*10**6)
	if self.min_freq > self.max_freq:
	    self.min_freq, self.max_freq = self.max_freq, self.min_freq # swap them
	    print "Start and stop frequencies order swapped!"
	self.fft_size = options.fft_size
	self.ofdm_bins = options.sense_bins
	# build graph
	s2v = gr.stream_to_vector(gr.sizeof_gr_complex, self.fft_size)
	mywindow = window.blackmanharris(self.fft_size)
	fft = gr.fft_vcc(self.fft_size, True, mywindow)
	power = 0
	for tap in mywindow:
	    power += tap*tap
	c2mag = gr.complex_to_mag_squared(self.fft_size)
	#log = gr.nlog10_ff(10, self.fft_size, -20*math.log10(self.fft_size)-10*math.log10(power/self.fft_size))
	# modifications for USRP2 
	if self.IS_USRP2:	
	    self.u = uhd.usrp_source(options.args,uhd.io_type.COMPLEX_FLOAT32,num_channels=1)		# Modified Line
	    # self.u.set_decim(options.decim)
	    # samp_rate = self.u.adc_rate()/self.u.decim()
	    samp_rate = 100e6/options.decim		# modified sampling rate
	    self.u.set_samp_rate(samp_rate)
	else:
	    self.u = gr.file_source(gr.sizeof_gr_complex,options.input_file, True)
	    samp_rate = 100e6 /options.decim		# modified sampling rate

	self.freq_step =0 #0.75* samp_rate
	self.min_center_freq = (self.min_freq + self.max_freq)/2
	
	global BW
	BW = self.max_freq - self.min_freq
	global size
	size=self.fft_size
	global ofdm_bins
	ofdm_bins = self.ofdm_bins
	global usr
	#global thrshold_inorder
	usr=samp_rate
	nsteps = 10 #math.ceil((self.max_freq - self.min_freq) / self.freq_step)
	self.max_center_freq = self.min_center_freq + (nsteps * self.freq_step)
	self.next_freq = self.min_center_freq
	tune_delay = max(0, int(round(options.tune_delay * samp_rate / self.fft_size))) # in fft_frames
	dwell_delay = max(1, int(round(options.dwell_delay * samp_rate / self.fft_size))) # in fft_frames
	self.msgq = gr.msg_queue(16)					# thread-safe message queue
	self._tune_callback = tune(self) 				# hang on to this to keep it from being GC'd
	stats = gr.bin_statistics_f(self.fft_size, self.msgq, self._tune_callback, tune_delay,
				      dwell_delay)			# control scanning and record frequency domain statistics
	self.connect(self.u, s2v, fft,c2mag,stats)
	if options.gain is None:
	    g = self.u.get_gain_range()
	    options.gain = float(g.start()+g.stop())/2			# if no gain was specified, use the mid-point in dB
	    
    def set_next_freq(self):
	target_freq = self.next_freq	#tx_success=0
        #start_time = 0
	#last_time = 0
	#count_init=0
	#nbytes = int(1e6 * options.megabytes)
	#n = 0
	#pkt_size = int(options.size)
	#carrier_map="FFFFFE7FFFFFF"
	#new_freq = options.tx_freq
	self.next_freq = self.next_freq + self.freq_step
	if self.next_freq >= self.max_center_freq:
	    self.next_freq = self.min_center_freq
	if self.IS_USRP2:
	    if not self.set_freq(target_freq):
	        print "Failed to set frequency to ", target_freq, "Hz"
	return target_freq
	
    def set_freq(self, target_freq):
	#return self.u.set_center_freq(target_freq)
	return self.u.set_center_freq(target_freq,0)
    def set_gain(self, gain):
	#self.u.set_gain(gain)
	self.u.set_gain(gain,0)
	
def sensor_init(options,Freq):
    tb1=sensor(options,Freq)
    return tb1
    
def sense_loop(tb,count):
    #fd= os.open('/home/spann/fifo',os.O_WRONLY) # Open the named pipe to pass on the sensed info to the transmitter part
    print "\n\nSensing the spectrum"
    tb.start()
    time.sleep(2)						# Added Line
    n = 1
    moving_avg_data = [0]*(size)
    avg_iterations = avg_iter_count = 10
    #new_data = [0]*(size/n) 			# This is decimated value of m.data avg of n terms at a time
    while count>0:
	count=count-1
	#hexa_thr=""
	m = parse_msg(tb.msgq.delete_head())			
	#for i in range(0,len(new_data)):
		#new_data[i] = sum(m.data[i*n:n*(i+1)])/float(n)
	if avg_iter_count > 0:
		#print avg_iter_count
		for i in range(0,size):
		      moving_avg_data[i] = moving_avg_data[i] + m.data[i]
		avg_iter_count = avg_iter_count - 1
	else: 
		for i in range(0,len(moving_avg_data)):
			moving_avg_data[i] = moving_avg_data[i]/float(avg_iterations)
		thrshold = map(lambda x: 0 if x>0.00010 else 1, moving_avg_data)		# Modified threshold	
		size2 = size/n
		thrshold_inorder= [0]*size2
		sensed_freq = [0]*size2
		ofdm_center_freq = m.center_freq # For now we are keeping the center freq of the ofdm same as that of sensing, will have to modify this later
		freq_resolution = usr/size2
		p = m.center_freq - freq_resolution*((size2/2)-1)
		#print "in else loop"
		#new_data= decimate_data(m.data,n)
		#p2=m.center_freq-usr/2
		#print p2
		#print usr
		for i in range(0,size2/2):
			sensed_freq[i]= p	
			print p,   moving_avg_data[i+size2/2],   thrshold[i+size2/2]
			#p=p+usr/(size2-1)
			p=p+freq_resolution
			thrshold_inorder[i] = thrshold[i+size2/2]
		
		for i in range(0,size2/2):
			sensed_freq[i+size2/2] = p
			print p,   moving_avg_data[i],   thrshold[i]
			#p=p+usr/(size2-1)
			p=p+freq_resolution
			thrshold_inorder[i+size2/2]= thrshold[i]
		#print 'End of one iteration'
		#print new_data
		#print m.data
		#print thrshold_inorder
		#Convert the vector into a string of Hexadecimal number
		hexa_thr = hex_conv(thrshold_inorder)
		#print hexa_thr
		avg_iter_count = avg_iterations
		moving_avg_data = [0]*(size)
		#os.write(fd,hexa_thr)
        #cla()
        #plot(thrshold_inorder)
    #print "hexa_thr=",hexa_thr
    tb.stop()
    tb.wait()
    return hexa_thr
        
#def decimate_data(data,n)        :
	#vec_mod = [0]*(len(data)/n)
	#for i in range(0,len(vec_mod)):
	  #vec_mod[i] = sum(data[i*n:n*(i+1)])/float(n)	  
	#print vec_mod 
	
# This function converts the vector of 1s and 0s into hexadecimal string for transmission  
def hex_conv(thrshold_inorder):
	dec_thr=0
	i=0
	hexa_thr=''
	abc = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
	length=len(thrshold_inorder)
	while ((i<length) & ((length-i)>=4)):
	    j=4
	    while(j>0):
	     if thrshold_inorder[i]==1:
	      dec_thr+= (2)**(4-j)
	      #print "dec_thr=",dec_thr
	     i=i+1
	     j=j-1
	    mul=dec_thr
	    #print "mul=",mul
	    dec_thr=0
	    hexa_thr_part = ''
	    while mul >15:
	     c = abc[mul%16]
	     hexa_thr_part = c+hexa_thr_part
	     mul = mul/16  
	    hexa_thr_part= abc[mul]+hexa_thr_part 
	    hexa_thr=hexa_thr+hexa_thr_part	   
	# print "hexa_thr=",hexa_thr
	return hexa_thr
	    
###################################################################################################################################################################        
	                                                 # Transmitter code
###################################################################################################################################################################        

def send_pkt(tb,payload='',carrier_map="FE7F",eof=False):
	#print "carrier_map_in_send_pkt=",carrier_map
	return tb.txpath.send_pkt(payload, eof,carrier_map) 

def run_transmiter(n,nbytes,count,carrier_map,tb,norestart,pkt_size):    
	tb.start()                       # start flow graph
	#tx_success=0
        #start_time = 0
	#last_time = 0
	#count_init=0
	#nbytes = int(1e6 * options.megabytes)
	#n = 0
	#pkt_size = int(options.size)
	#carrier_map="FFFFFE7FFFFFF"
	#new_freq = options.tx_freq
	pktno = 0
	print "\n\nTransmitting in", Freq.value ,"Hz"
	print "Carrier map = ",carrier_map
	# print "carrier_map_passed_by_main=",carrier_map
	# sound=open('sound','w')
        while n < nbytes:
	  	if string.count(carrier_map,'0') >= 15:
		    sys.stderr.write('Primary Transmission detected\n')
		    #tb.stop()
		    #tb.wait()
		    norestart.value=0
	        #if count_init >2000:
	##	carrier_map_new=string_pipe.readline()
        ##      carrier_map_new=carrier_map[0:(len(carrier_map)-1)] 
		    #if (pktno%40000)==0:
			##carrier_map = os.read(fd,options.occupied_tones/4) #The sensor is a part of this code so no need to read from pipe 
			#if string.count(carrier_map,'0') >= 180:
			    #carrier_map="000000000000"
			    #tx_success=tb.txpath.sink.set_center_freq(new_freq+16)
			    #if tx_success:
			      #new_frew=new_freq+1e6
			      #print "successfully"
			    #print "Freq changed to "
			    #print new_freq
		    #return n
                #if options.from_file is None:
		#	data = (pkt_size - 2) * chr(pktno & 0xff) 
		#else:
		#if pktno < 19:
		    #data = (pkt_size - 2) * chr(pktno & 0xff)
		#else:
		    #print "qlength=",src_sound.msgq.count()
		    #mdata =src_sound.msgq.delete_head()
		    #msg_type=mdata.type()
		    #print "mdata=",mdata
		    #data=mdata.to_string()
		    ##print "print data=%r" %(data)
	            #l=len(data)/4
	            #fdata = struct.unpack('%df' % (l,), data)
	        #sys.stdin.read() #raw_input()
                #print "udata",udata
		    #if data == '':
			    #break;   
	        udata ="Hi, I am Kranthi" 
	        if (count==0):
                       break;                             
		count=count-1
		#count_init=count_init + 1
		pktno=pktno+1
		#print "count=",count
		for i in range(0,40):
		    # print "i",i
		    if (i<1):
		      data = 'sync'+(pkt_size - 6) * chr(pktno & 0xff)
		    else:
		      data=udata
		    #  print "data",data
		    payload = struct.pack('!H', pktno & 0xffff) + data
		    #print "length of payload=",len(payload)
		    # print "payload",payload
		    send_pkt(tb,payload)
		    #n += len(payload)
		    #print "n=",n
		    #print "count=",count
		    #sys.stderr.write('.')
		    #if options.discontinuous and pktno % 10 == 1:
			    #time.sleep(1)
		    pktno += 1   
		sys.stderr.write('.')  
		n += len(payload)
	  #send_pkt(eof=True)
	tb.stop()
	tb.wait()
	#print "count before returning from trans call=",count
	return n
 
def Start_transmitter(Freq,norestart):             
	  trans=trans_init(Freq)
	  Data_in_MB=trans.Data()
	  options=trans.return_options()
	  # occupied_tones=options.occupied_tones
	  # print "occupied_tones=",occupied_tones
	  tb1=sensor_init(options,Freq)
	  pkt_size=int(options.size)
	  tb=trans.return_obj()
	  nbytes = int(1e6 * Data_in_MB)
	  count=10 #number of packets to send before sensing
	  count1=20 #number of times the sensor loop will run
	  carrier_map_new="FE7F" #initial carrier map 
	  #carrier_map_new="FFFFFE7FFFFFF" #initial carrier map
	  n=0
	  while(n < nbytes):
		  n=run_transmiter(n,nbytes,count,carrier_map_new,tb,norestart,pkt_size)
		  carrier_map_new=sense_loop(tb1,count1)
		  #print "count after returning form trans call=",count
		  #run the sensing code now and return the new carier map
		  #print "carrier_map_new_before_clipping",carrier_map_new
		  #carrier_map_new=carrier_map_new[0:150]
		  #print "carrier_map_new",carrier_map_new
		  #print "n=", n
		  #print "nbytes=",nbytes
	  send_pkt(tb,"",carrier_map_new,eof=True)                     
                
if __name__ == '__main__':
	try:
	  norestart=Value('i',1)
	  Freq=Value('i',900*10**6)
	  mp=Process(target=Start_transmitter,args=(Freq,norestart))
	  mp.start()
	  p=Process(target=transmitter_control,args=(mp,Freq,norestart))
          p.start()	        
	except KeyboardInterrupt:
		pass
