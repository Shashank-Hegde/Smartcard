#ifndef INV_AES
#define INV_AES

#include <avr/io.h>
#include <inttypes.h>
#include <string.h>
#include <stdbool.h>
/**
 AES Implementation With Masking:
*/



//Funktions:


/************************************************************************/
/* Look                                                                     */
/***************************
 * *********************************************/
void inv_mixColumns(uint8_t state[16]);
void inverseByteSubShiftRow(uint8_t plainText[16]);
void inv_aes128_unmasked(uint8_t state[16]);

#endif

