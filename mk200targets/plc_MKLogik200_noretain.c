#include <stdio.h>

int CheckRetainBuffer(void)
{
	printf("CheckRetainBuffer\r\n");
	return 1;
}

void ValidateRetainBuffer(void)
{
	printf("ValidateRetainBuffer\r\n");
}

void InValidateRetainBuffer(void)
{
	printf("InValidateRetainBuffer\r\n");
}

void Retain(unsigned int offset, unsigned int count, void *p)
{
	printf("Retain: %u, %u, %x\r\n", offset, count, (unsigned int)*p);
}

void Remind(unsigned int offset, unsigned int count, void *p)
{
	printf("Remind: %u, %u, %x\r\n", offset, count, (unsigned int)*p);
}
