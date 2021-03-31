#!/usr/bin/env python

import sys

def parseContent(content):
    my_array=content.split("[wiki:")
    if len(my_array)>1:
        my_link=my_array[1].split("]")
        my_info=my_link[0].split(" ")
        if len(my_info)>1:
            my_link[0]="[/ZOO-Project/ZOO-Project/wiki/"+my_info[0]+" "+(" ".join(my_info[1:]))+"]"
            my_array[1]=my_link[0]+("]".join(my_link[1:]))
            return my_array[0]+("[wiki:".join(my_array[1:]))
        else:
            my_link[0]="[["+my_link[0]+"]]"
            my_array[1]=my_link[0]+("]".join(my_link[1:]))
            return my_array[0]+("[wiki:".join(my_array[1:]))

    return content

my_content=None
with open(sys.argv[1], 'r', encoding="utf-8") as my_file:
    my_content=my_file.read()

cnt=0
pre_content=parseContent(my_content)
while pre_content.count("[wiki:")>0:
    pre_content=parseContent(pre_content)
    cnt+=1

print(pre_content)
