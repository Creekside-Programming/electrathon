#include <iostream>
#include <RadioLib.h>
#include <hal/RPiPico/PicoHal.h>

// SPI pins
// todo: these are all made up find the real ones
#define SPI_PORT  spi0
#define PIN_MISO  16
#define PIN_MOSI  19
#define PIN_SCK   18

// radio pins
#define CS_PIN 13
#define IRQ_PIN 14 // dio9
#define RESET_PIN 5
#define BUSY_PIN 14 // todo: this is the same as IRQ, i must've traced wires wrong this must be changed

PicoHal* hal = new PicoHal(SPI_PORT, PIN_MISO, PIN_MOSI, PIN_SCK);

Module mod(hal, CS_PIN, IRQ_PIN, RESET_PIN, BUSY_PIN);
LR1121 radio(&mod);

int main() {
    std::cout << "hello world" << std::endl;

}