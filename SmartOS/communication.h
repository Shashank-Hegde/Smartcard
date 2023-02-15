/*
 * communication.h
 *
 *  Created on: Dec 6, 2022
 *      Author: Usama
 */

#include <avr/io.h>

#ifndef COMMUNICATION_H_
#define COMMUNICATION_H_

void comm_initialization();
void transmit_data(uint8_t* bytes, uint8_t length);
void transmit_byte(uint8_t byte);
uint8_t receive_data();

#endif /* COMMUNICATION_H_ */
