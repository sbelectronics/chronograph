/* 
 * boostconv.c
 *
 * 30V boost converter
 *
 * (c) Scott Baker, https://www.smbaker.com/
 */

//#define F_CPU 14745600

#include <stdio.h>

#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>
#include <inttypes.h>

#include <util/delay.h>

//PIN configuration
// PB0 - Enable
// PB1 - Out
// PB2 - feedback
// PB3 - trimmer

#define BIT_ENABLE (1<<PB0)
#define BIT_OUT (1<<PB1)
#define BIT_FEEDBACK (1<<PB2)
#define BIT_TRIMMER (1<<PB3)

#define OUT_LOW PORTB &= ~BIT_OUT
#define OUT_HIGH PORTB |= BIT_OUT

#define PWM_MAX 159

#define LOW 0
#define HIGH 1

uint8_t readADC(uint8_t mux)
{
    ADMUX =
            (1 << ADLAR) |     // left shift result
            (0 << REFS1) |     // Sets ref. voltage to VCC, bit 1
            (0 << REFS0) |     // Sets ref. voltage to VCC, bit 0
            (mux << MUX0);    

    ADCSRA =
            (1 << ADEN)  |     // Enable ADC
            (1 << ADPS2) |     // set prescaler to 64, bit 2
            (1 << ADPS1) |     // set prescaler to 64, bit 1
            (0 << ADPS0);      // set prescaler to 64, bit 0

    ADCSRA |= (1 << ADSC);         // start ADC measurement
    while (ADCSRA & (1 << ADSC) ); // wait till conversion complete

    return ADCH;
}

uint8_t readAverageADC(uint8_t mux, uint8_t count)
{
    uint16_t accum;
    uint8_t i;

    accum = 0;
    for (i=0; i<count; i++) {
      accum = accum + readADC(mux);
      _delay_us(10);
    }

    return accum/count;
}

int main() {
    uint8_t currentPwm;

    // make the out pin an output
    DDRB |= BIT_OUT;
    OUT_LOW;

    // 100 KHz PWM on output pin
    PLLCSR = 6;
    TCCR1 = 0xE3;  // 11100011 PCK/4
    GTCCR = 0;
    OCR1C = PWM_MAX; 
    OCR1A = 0;

    currentPwm = 0;
    while(1) {
        int feedback = readAverageADC(1, 4);
        int setpoint = readADC(3);

        if (feedback < setpoint) {
            if (currentPwm < (PWM_MAX-20)) {
              currentPwm ++;
            } 
        } else {
            if (currentPwm > 0) {
              currentPwm --;
            }
        }
        OCR1A = currentPwm;
    }

    return 0;
}
