// Host execution of the production controller header, not an ESP32/I2C emulator.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "controller.h"
int checks=0;
void expect(bool ok,const char* message) {
    ++checks; if (!ok) { std::fprintf(stderr,"FAILED: %s\n",message); std::exit(1); }
}
Sample sample(float v=12.8f,float a=.5f,float w=6.4f,float t=28) {
    Sample s; s.valid=true; s.batteryV=v; s.batteryA=a; s.loadW=w; s.temperatureC=t; return s;
}
int main() {
    Sample s=sample(); Controller c;
    c.update(s,.1f); expect(!c.optionalOn && !isfinite(c.socPct),"boot unknown/off");
    c.syncFull(); expect(c.restore(s)==HARDWARE_CONFIRMED,"hardware lock controls restore");
    c.optionalOn=true; c.update(s,.1f);
    expect(c.optionalOn==HARDWARE_CONFIRMED,"production lock enforced during update");
    for (float value : {float(NAN), 2.1f, -2.1f}) {
        Controller f; f.syncFull(); f.optionalOn=true; Sample bad=s; bad.batteryA=value;
        f.update(bad,.1f); expect(!f.optionalOn && !isfinite(f.socPct),"invalid current clears reference");
    }
    for (float dt : {0.f,2.1f,float(NAN)}) {
        Controller f; f.syncFull(); f.optionalOn=true; f.update(s,dt);
        expect(!f.optionalOn && !isfinite(f.socPct),"invalid dt clears reference");
    }
    Controller balance; balance.socPct=80;
    for (int i=0;i<3600;i++) balance.update(sample(12.8,1,12.8),1);
    expect(fabsf(balance.socPct-(80.f-100.f/6))<.05f,"one hour discharge charge balance");
    for (int i=0;i<3600;i++) balance.update(sample(12.8,-1,4),1);
    expect(fabsf(balance.socPct-(80.f-100.f/6+100.f*.98f/6))<.1f,"one hour charge balance");
    expect(!isfinite(balance.runtimeH),"charging runtime is unknown, never negative");
    // Use the actual 10 Hz integration cadence, especially at small currents.
    for (float current : {.005f, .1f, .5f}) {
        Controller precision; precision.socPct=80;
        for (int i=0;i<36000;i++) precision.update(sample(12.8,current,4),.1f);
        const double expected=80.0-100.0*current/6.0;
        expect(fabs(precision.socPct-expected)<.005,"10 Hz charge integration retains small increments");
    }
    Controller finite; finite.syncFull(); Sample invalid=s; invalid.temperatureC=NAN;
    expect(!finite.restore(invalid),"NaN temperature rejects restore even with valid flag");
    if (HARDWARE_CONFIRMED) {
        Controller delay; delay.socPct=30; delay.optionalOn=true;
        for (int i=0;i<29;i++) delay.update(s,.1f);
        expect(delay.optionalOn,"load retained before 3 seconds");
        delay.update(s,.1f); expect(!delay.optionalOn,"load shed at 3 seconds");
        delay.update(sample(12.8,.1,1.28),.1f);
        expect(!delay.optionalOn && std::strcmp(delay.state,"PRIORITY")==0,"shed remains latched");
        expect(!delay.restore(s),"restore evaluates full prospective load");
        delay.syncFull(); expect(delay.restore(s),"explicit restore with margin");
        for (float v : {11.6f,11.0f,14.8f}) {
            Controller f; f.syncFull(); f.optionalOn=true; f.update(sample(v),.1f);
            expect(!f.optionalOn && std::strcmp(f.state,"RESERVE")==0,"voltage limits switch load off");
        }
        Controller heat; heat.syncFull(); heat.optionalOn=true; heat.update(sample(12.8,.5,6.4,45),.1f);
        expect(!heat.optionalOn && std::strcmp(heat.state,"TEMPERATURE")==0,"temperature limit");
        Controller recover; recover.syncFull(); recover.optionalOn=true; Sample bad=s; bad.valid=false;
        recover.update(bad,.1); recover.update(s,.1);
        expect(!recover.optionalOn && !isfinite(recover.socPct),"fault recovery requires new reference");
        Controller gap; gap.syncFull(); gap.optionalOn=true; gap.minimumRuntimeH=10;
        gap.update(s,1); gap.update(s,1); gap.update(sample(12.8,.5,6.4,46),.1);
        gap.update(s,1); expect(std::strcmp(gap.state,"WATCH")==0,"thermal event resets sustained timer");
    }
    std::printf("{\"status\":\"PASS\",\"hardware_confirmed_in_test_copy\":%s,\"assertions\":%d}\n",HARDWARE_CONFIRMED?"true":"false",checks);
}
