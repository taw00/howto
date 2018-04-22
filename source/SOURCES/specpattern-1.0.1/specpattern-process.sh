#!/usr/bin/bash

# I can write this loop two ways...
# example 1
#while
#  _date=$(date +%F\ %R:%S)
#  printf "$_date Hello. I am the specpattern process example. I repeat this statement every 10s.\n"
#  sleep 10s
#do
# :;
#done

# example 2 - maybe more nature
while [ anything ]
do
  _date=$(date +%F\ %R:%S)
  printf "${_date}\n"
  printf "    Hi! I'm the specpattern process example!\n"
  printf "    I repeat this statement every 10s.\n"
  sleep 10s
done

