/*
 * define.h
 *
 *  Created on: Dec 5, 2022
 *      Author: shubhamjmishra
 */

#ifndef DEFINE_H_
#define DEFINE_H_

#include<avr/io.h> //AVR device-specific IO definitions, in our case iom644.h

#define SetBit(PORT, BIT)	PORT |= (1<<BIT)
#define ClrBit(PORT, BIT)	PORT &= ~(1<<BIT)
#define TglBit(PORT, BIT)	PORT ^= (1<<BIT)
#define GetBit(PIN, BIT)	((PIN & (1<<BIT))?true:false)

#define trig_start_pb4()	{SetBit(DDRB, PB4); ClrBit(PORTB, PB4);} // trigger initialize Data Direction Register
#define trig_high()	SetBit(PORTB, PB4) // Set trigger pin to High
#define trig_low()	ClrBit(PORTB, PB4) // Set trigger pin to Low
#define trig()		{SetBit(PORTB, PB4); ClrBit(PORTB, PB4);}

#define SIZE(a)	sizeof(a)/sizeof(a[0])

#endif /* DEFINE_H_ */
