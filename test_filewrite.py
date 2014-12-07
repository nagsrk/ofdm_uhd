#!/usr/bin/env python
fd= open('check','a')
str1 = 'Rohit'
str2 = 'Kamath'
i =0
while i<100:
    if (i%2) == 0:
      fd.write(str1)
    else:
      fd.write(str2)
    i=i+1
