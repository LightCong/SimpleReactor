#!/bin/bash
total=0
function getdir(){
    for element in `ls $1`
    do  
        dir_or_file=$1"/"$element
        if [ -d $dir_or_file ]
        then 
            getdir $dir_or_file
        else
        	if [ "${dir_or_file##*.}" = "py" ]
        	then
        		x=`cat $dir_or_file|wc -l`
        		echo $dir_or_file,$x
        		total=$[x+total]
        	fi
        	
        fi  
    done
}
root_dir="./"
getdir $root_dir
echo $total