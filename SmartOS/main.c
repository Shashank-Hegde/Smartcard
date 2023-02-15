/*
 * main.c
 *
 *  Created on: Dec 6, 2022
 *      Author: shubhamjmishra
 */

#include <avr/interrupt.h>  //for disabling interrupts in order to perform required operations.
#include "define.h"
#include "iso_standard.h"
#include "uart.h"
#include "communication.h"



int main()
{
	trig_start_pb4(); //toggles the trigger pin at PORTB4 in ATMega644.
	uart_initialization();
	comm_initialization();
//aes128_init(key, &ctx);

	sei(); //This function enables interrupts by setting the global interrupt mask

    //State machine
	answer_to_reset_transmit();

	for(;;)  //‘C’s infinite loop statement, similar to while(1).
	{
		card_authenticator();
	}
}
