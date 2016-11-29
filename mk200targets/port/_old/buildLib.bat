arm-none-eabi-gcc -mcpu=cortex-m3 -mlittle-endian -mthumb -g -D STM32F407xx -c src/syscalls.c -o syscalls.o
arm-none-eabi-gcc -mcpu=cortex-m3 -mlittle-endian -mthumb -g -D STM32F407xx -c src/startup_stm32f407xx.s -o startup_stm32f407xx.o
arm-none-eabi-gcc -mcpu=cortex-m3 -mlittle-endian -mthumb -I"./inc" -g -D STM32F407xx -c src/system_stm32f4xx.c -o system_stm32f4xx.o
