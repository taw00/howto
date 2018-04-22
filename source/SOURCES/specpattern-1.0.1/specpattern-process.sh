#!/usr/bin/bash

SECONDS=10

# I can write this loop two ways...
# example 1
#while
#  _date=$(date +%F\ %R:%S)
#  printf "$_date - Hi! I am the specpattern process. I repeat this statement every ${SECONDS}s.\n"
#  sleep ${SECONDS}s
#do
# :;
#done

# example 2 - maybe more nature
while [ anything ]
do
  _date=$(date +%F\ %R:%S)
  printf "${_date} - Hi! I'm the specpattern process! I repeat this statement every ${SECONDS}s.\n"
  sleep ${SECONDS}s
done

