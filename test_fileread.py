#!/usr/bin/env python
fd= open('check','r')
str1 = ''
str2 = ''
i =0
while i<100:
    if (i%2) == 0:
      fd.read(str1)
    else:
      fd.read(str2)
    i=i+1
