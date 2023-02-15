/*
 * iso_standard.h
 *
 *  Created on: Dec 12, 2022
 *      Author: shubhamjmishra
 */

#include<avr/io.h>

#ifndef ISO_STANDARD_H_
#define ISO_STANDARD_H_

void answer_to_reset_transmit();
void card_authenticator();
void smartcard_terminal_get_reply(uint8_t* authenticator);
void smartcard_terminal_reply(uint8_t* authenticator_reply);
void sequence_detector(const uint8_t* data, const uint8_t data_length);



#endif /* ISO_STANDARD_H_ */
