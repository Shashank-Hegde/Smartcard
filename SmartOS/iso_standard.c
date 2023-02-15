/*
 * iso_standard.c
 *
 *  Created on: Dec 12, 2022
 *      Author: shubhamjmishra
 */

#include "iso_standard.h"
#include "define.h"
#include "uart.h"
#include "communication.h"

#include "aes/inv_aes.h"

#include <stdbool.h>
#include <string.h>
#include <stdio.h>
#include <util/delay.h>

//const uint8_t key[16] = {}; //enter the key here
//aes128_ctx_t ctx;

void answer_to_reset_transmit()
{
	const uint8_t answer_to_reset[] = {0x3B, 0x90, 0x11, 0x00}; // Lab Manual - Answer To Reset, TS = 0x3B, T0 = 0x90, TA1 =0x11 and TD1 = 0x00
	transmit_data((uint8_t*) answer_to_reset, SIZE(answer_to_reset));  //usama
}

void card_authenticator() // protocol challengese to the card reader
{
	uint8_t authenticator[16];

	smartcard_terminal_get_reply(authenticator);

	uint8_t* authenticator_reply = authenticator;

	trig_high();
//aes128_dec(authenticator, &ctx);
	inv_aes128_unmasked(authenticator);
	trig_low();

	uint8_t reply[] = {0x61, 0x10}; ////send after key reception
	transmit_data(reply, SIZE(reply));

	smartcard_terminal_reply(authenticator_reply);
}

void smartcard_terminal_get_reply(uint8_t* authenticator) //takes the protocol response from card reader
{
	const uint8_t sequence[] = {0x88, 0x10, 0x00, 0x00, 0x10}; //APDU
	sequence_detector(sequence, SIZE(sequence));

	for(int i = 0; i < 16; i++)
	{
		transmit_byte(0xEF);
		authenticator[i] = receive_data();
	}

}

void smartcard_terminal_reply(uint8_t* authenticator_reply) //takes the protocol response from card reader
{
	uint8_t sequence[] = {0x88, 0xC0, 0x00, 0x00, 0x10}; //APDU
	sequence_detector(sequence, SIZE(sequence));

	transmit_byte(0xC0);
	transmit_data(authenticator_reply, 16); // we know that authenticator_reply will always be 16bytes long.

	const uint8_t reply[] = {0x90, 0x00}; //send after the Key Transmit
	transmit_data((uint8_t*) reply, SIZE(reply));
}

void sequence_detector(const uint8_t* data, const uint8_t data_length)
{
	for(int i = 0; i < data_length; i++)
	{
		uint8_t sequence_expected = data[i];
		uint8_t sequence_received = receive_data();
		if(sequence_expected != sequence_received){
			char buf[50];
			sprintf(buf, "Received %02X instead of %02X at byte %d", sequence_received, sequence_expected, i);
			assert(false, buf); // Receive Unexpected Data
		}
	}
}
