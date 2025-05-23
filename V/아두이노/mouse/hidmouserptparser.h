#if !defined(__HIDMOUSERPTPARSER_H__)

#define __HIDMOUSERPTPARSER_H__

#include <usbhid.h>

void onButtonUp(uint16_t buttonId) __attribute__((weak));
void onButtonDown(uint16_t buttonId) __attribute__((weak));
void onTiltPress(int8_t tiltValue) __attribute__((weak));
void onMouseMove(int16_t xMovement, int16_t yMovement, int8_t scrollValue) __attribute__((weak));
void onScroll(int8_t scrollValue) __attribute__((weak));

class HIDMouseReportParser : public HIDReportParser
{
	uint8_t previousButtonsState;
public:
	HIDMouseReportParser(void *);
	virtual void Parse(USBHID *hid, bool is_rpt_id, uint8_t len, uint8_t *buf);
};

#endif//__HIDMOUSERPTPARSER_H__
