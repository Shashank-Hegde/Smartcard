/*
 * uart.h
 *
 *  Created on: Dec 6, 2022
 *      Author: Usama
 */

#ifndef UART_H_
#define UART_H_

#include <stdbool.h>

void uart_initialization();
void uart_put_char(const char c);
void uart_put_string(const char* c_str);

void assert(bool cond, const char* error_string);

#endif /* UART_H_ */
