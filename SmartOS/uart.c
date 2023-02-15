/*
 * uart.c
 *
 *  Created on: Dec 6, 2022
 *      Author: Usama
 */


#include "uart.h"
#include "define.h"

#include <avr/io.h>
#include <avr/interrupt.h>

#include <string.h>


void uart_initialization()
{
	// Configuring the maximum speeed
	UBRR0 = 0;
	SetBit(UCSR0A, U2X0);

	SetBit(UCSR0B, TXEN0); // Enabling transmit mode

	// The recieve pin is set as debug
	SetBit(DDRD, PD0);
	ClrBit(PORTD, PD0);
}

void uart_put_char(const char c)
{
	while (!GetBit(UCSR0A, UDRE0)); // Waiting for the buffer to be free
	UDR0 = c;
}

//Transmitting string
void uart_put_string(const char* s)
{
	while(*s) {
		uart_put_char(*s++);
	}
}

void assert(bool cond, const char* error_string)
{
	if(!cond)
	{
		// Incrementing the error counter
		if(PORTA == 0x00)
		{
			PORTA = 0x01;
		} else {
			PORTA ++;
		}

		// Print error message
		uart_put_string(error_string);
	}
}
