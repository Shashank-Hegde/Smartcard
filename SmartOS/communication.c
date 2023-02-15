/*
 * communication.c
 *
 *  Created on: Dec 6, 2022
 *      Author: Usama
 */

#include "communication.h"

#include <stdbool.h>

#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <util/parity.h>

#include <string.h>

#include "define.h"
#include "uart.h"

enum mode_t {RECEIVE, TRANSMIT};

volatile enum mode_t mode = RECEIVE;
volatile uint8_t bit_received_counter = 0;
volatile uint8_t curr_byte_received = 0x00;
volatile bool byte_received = false;
volatile bool next_bit_sending = false;
volatile bool bit_sent = true; // True initially for sending immediately


// Pin Change Interrupt Request 1
ISR(PCINT1_vect)
{
	if(bit_received_counter != 0)
	{
		// We should not come here as there should be a start bit
		return;
	}

	if(GetBit(PINB, PB6) != 0)
	{
		// The clock is falling edge so rising edge is not correct
		// It can be triggered by the parity bit of falling edge in which case we ignore
		// or it is bad, in case we missed a byte.
		return;
	}

	if(mode == RECEIVE)
	{
		// Starting the timer after the start bit.
		// We would receive 8 data bits with 1 even parity
		SetBit(TCCR1B, CS10); // Set clock source to CPU/1 = enable timer
		TCNT1 = 0;

		bit_received_counter = 0;
		curr_byte_received = 0x00;

		OCR1A = 372*1.50-100; // Wait 1 (start bit) + 0.5 etu for sampling
		// 0.5 etu is so that we go to the middle of next bit for sampling

		// Disabling the interrupt so that we do not come here again after recieving a bit
		ClrBit(PCICR,PCIE1);
		ClrBit(PCMSK1,PCINT14);
	}
}


ISR(TIMER1_COMPA_vect)
{
	switch(mode)
	{

	case RECEIVE:
		if(bit_received_counter == 0)
		{
			OCR1A = 372; // this will happen in the middle of bit 0. from now on, sample every 1 ETU.
		}

		if(bit_received_counter < 8) // data bit
		{
			// sampling 7 times and doing a majority decision
			int8_t sample_value = 0;
			sample_value += (GetBit(PINB, PB6))?1:-1;
			sample_value += (GetBit(PINB, PB6))?1:-1;
			sample_value += (GetBit(PINB, PB6))?1:-1;
			sample_value += (GetBit(PINB, PB6))?1:-1;
			sample_value += (GetBit(PINB, PB6))?1:-1;
			sample_value += (GetBit(PINB, PB6))?1:-1;
			sample_value += (GetBit(PINB, PB6))?1:-1;

			sample_value = (sample_value>0)?1:0;
			// save the bit
			curr_byte_received |= (sample_value<<(bit_received_counter++));

		}
		else if (bit_received_counter == 8) // parity bit
		{
			// sampling 7 times and doing a majority decision
			int8_t sample_value = 0;
			sample_value += (GetBit(PINB, PB6))?1:-1;
			sample_value += (GetBit(PINB, PB6))?1:-1;
			sample_value += (GetBit(PINB, PB6))?1:-1;
			sample_value += (GetBit(PINB, PB6))?1:-1;
			sample_value += (GetBit(PINB, PB6))?1:-1;
			sample_value += (GetBit(PINB, PB6))?1:-1;
			sample_value += (GetBit(PINB, PB6))?1:-1;

			sample_value = (sample_value>0)?1:0;

			assert(sample_value == parity_even_bit(curr_byte_received), "WP"); // Wrong Parity

			// Byte has been received
			byte_received = true;
			bit_received_counter = 0;
			ClrBit(TCCR1B, CS10); // Disabling the clock
		}
		break;


	case TRANSMIT:
		if(next_bit_sending) //If we have to sent 1
		{
			// Sending 1 by changing the pin to input (high Z)
			ClrBit(DDRB, PB6);
		} else {
			// Sending 0 by changing the input to zero and driving low
			SetBit(DDRB, PB6);
			ClrBit(PORTB, PB6);
		}
		bit_sent = true;
		break;

	}
}

void receive_mode()
{
	// Set receiving mode
	mode = RECEIVE;
	byte_received = false;
	ClrBit(DDRB, PB6); // PDI_DATA as input
	SetBit(PORTB, PB6); // Activating pull up
	SetBit(PCICR,PCIE1); // Enabling pin change interrupt
	SetBit(PCMSK1,PCINT14); // Enabling pin change interrupt for PDI_DATA pin
}

void transmit_mode()
{
	// Set transmitting mode
	mode = TRANSMIT;
	ClrBit(PCICR,PCIE1); // disable pin change interrupt
	ClrBit(PCMSK1,PCINT14); // disable pin change interrupt for PDI_DATA pin
	SetBit(DDRB, PB6); // set PDI_DATA as output
}

void comm_initialization()
{
	// In receive mode
	ClrBit(DDRB, PB6); // set PDI_DATA as input
	SetBit(PORTB, PB6); // activating internal pullup
	PCICR |= (1<<PCIE1); // Pin change interrupt enabled
	PCMSK1 |= (1<<PCINT14); // Pin change interrupt enabled for PDI_DATA pin

	//Init timer 1
	SetBit(TCCR1B, WGM12); // Set CTC Mode
	OCR1A = 372; //Count to 372 (1 etu)
	SetBit(TIMSK1, OCIE1A); // Interrupt no reaching OCR1A
}


// sends a bit via the PDI line. waits until 372 clock (1 ETU) have passed.
void send_bit(bool bit)
{
	while(!bit_sent); // waiting for the last pin to go
	bit_sent = false; // Block the pin
	next_bit_sending = bit; // Sending the bit in 372 cycles
}

void transmit_data(uint8_t* bytes, uint8_t length)
{
	while(length--) transmit_byte(*(bytes++));
}

void transmit_byte(uint8_t byte)
{
	uint8_t parity = 0;

	transmit_mode();
	TCNT1 = 0;
	SetBit(TCCR1B, CS10); // Enable clock for timer

	// Due to 12 ETU limit b/w start bits, wait 3 etu
	for(int i = 0; i < 3; i++)
	{
		send_bit(true);
	}

	// Sending the start bit (low)
	send_bit(false);

	// Shifting bit 8 times and masking
	for(uint8_t i = 0x01; i != 0; i <<= 1)
	{
		send_bit (byte & i);
		if(byte & i) parity = !parity;
	}

	// Sending even parity
	send_bit(parity);

	// Make sure it is sent
	while(!bit_sent); // wait until last bit was sent
	_delay_loop_2(372/4); // 1 ETU

	ClrBit(TCCR1B, CS10); // Disable clock source of timer

	// Receive mode
	receive_mode();
}

uint8_t receive_data()
{
	receive_mode();
	while(!byte_received);
	return curr_byte_received;
}
