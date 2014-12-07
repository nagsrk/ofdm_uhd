# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gnuradio import gr, blks2
from gnuradio import usrp2,window,audio
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import string
import os
import time, struct,sys,multiprocessing 

class Read_bit_string(self,fft_length):
         self.__init__(self):
	   self.fd1=os.open('fifo',O_RDONLY)
	   self.fd2=os.open('Time_fifo',O_RDONLY)
	 
	 def read(self):
	    carrier_str=os.read(fd1,fft_length)
	    time=os.read(fd2,10)
	    time=float(time)
	    return carrier_str,time
	    

def find_channels(minimum_bandwidth_req,bin_size,fft_length):
         min_numof_zeros=ceil(minimum_bandwidth_req/bin_size)
         potential_channel_list=[]
         string_potential_channels=""
         n=0
         req_bit_pattern=[0]*min_numof_zeros
         count=0
         read_carrier=Read_bit_string(fft_length)
         carrier_str_list=[]
         time_list=[]
         channel_list=[]
        
         while(count<=400):
	   [carrier_str,time]=read_carrier.read()
	   carrier_str_list.append([carrier_str,time])
	         while (n<= len(carrier_str)-(min_numof_zeros)):
		    index=carrier_str.find(req_bit_pattern,n)
		    if (index!=-1) and (str(index) not in potential_channel_list):
			potential_channel_list.append(str(index))
			string_potential_channels=string_potential_channels+str(index)
		    n=n+index
	
	if (len(string_potential_channels)/len(potential_channel_list))>=160): #160=40 % of 400 ie there shoul be at least holes 40% of the time
	       print "found channels\n"
	       for channel in potential_channels_list:
		   count =string_potential_channels.count()
		   if (count>=160):
		     channel_list.append(channel)
		print "channels found",channel_list
		return carrier_str_list, channel_list
	else  
	print "no channels found\n changing band"
	# send info to the sensor program using pipe to switch to next freq.
	return -1,-1,-1
	

def create_channel_state_graph(channel_number,carrier_str_list,min_numof_zeros):
	  channel_graph=[]
	  offset=channel_number+min_numof_zeros
	  for channel_str in channel_str_list:
	      if channel_str[0][channel_number:offset].count('0')<(min_numof_zeros-1):
		 channel_graph.append([0,channel_str[1]])
	      else
                 channel_graph.append([1,chanel_str[1]])	
                 
	  
	
	       
	     
