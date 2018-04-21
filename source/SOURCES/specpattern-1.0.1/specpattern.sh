#!/usr/bin/bash

# I can write this loop two ways...
# example 1
#while
#  _date=$(date +%F\ %R:%S)
#  echo "$_date Hello. I am the specpattern process example. I repeat this statement every 10s."
#  sleep 10s
#do
# :;
#done

# example 2 - maybe more nature
while [ anything ]
do
  _date=$(date +%F\ %R:%S)
  echo "$_date Hello. I am the specpattern process example. I repeat this statement every 10s."
  sleep 10s
done

