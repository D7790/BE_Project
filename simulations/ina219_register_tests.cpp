#include <cstdio>
#include <cstdlib>
#include <cmath>
#include "ina219_checked.h"
int checks=0;
void expect(bool ok,const char* what) { ++checks; if(!ok) {std::fprintf(stderr,"FAILED: %s\n",what);std::exit(1);} }
struct Fake {
    int reads=0,fail=-1,reset=-1;
    uint16_t config=0x399f,cal=4096,bus=uint16_t(3200<<3)|2,shunt=5000,current=5000;
    bool operator()(uint8_t reg,uint16_t& value) {
        int n=reads++;
        if(n==fail)return false;
        if(n==reset){config=0x399f;cal=0;}
        switch(reg){case 0:value=config;break;case 5:value=cal;break;case 2:value=bus;break;case 1:value=shunt;break;case 4:value=current;break;default:return false;}
        return true;
    }
};
bool run(Fake& f,Ina219Reading& out) {
    return readIna219Checked([&f](uint8_t r,uint16_t& v){return f(r,v);},out);
}
int main(){
    Ina219Reading out; Fake f;
    expect(run(f,out),"valid registers accepted");
    expect(std::fabs(out.busV-12.8)<1e-5 && std::fabs(out.shuntV-.05)<1e-6 && std::fabs(out.currentA-.5)<1e-6,"scales and sign");
    Fake negative;negative.current=uint16_t(65536-7500);negative.shunt=uint16_t(65536-7500);
    expect(run(negative,out) && std::fabs(out.currentA+.75)<1e-6 && std::fabs(out.shuntV+.075)<1e-6,"negative current decoded");
    for(int n=0;n<8;n++) {
        Fake broken;broken.fail=n;out.currentA=123;
        expect(!run(broken,out) && !std::isfinite(out.currentA),"any failed transaction invalidates complete reading");
    }
    Fake overflow;overflow.bus|=1;expect(!run(overflow,out),"math overflow rejected");
    Fake wrong;wrong.config=0x399e;expect(!run(wrong,out),"changed conversion mode rejected");
    Fake zero;zero.cal=0;expect(!run(zero,out),"lost calibration rejected");
    Fake changed;changed.cal=8192;expect(!run(changed,out),"different current LSB rejected");
    for(int n=0;n<8;n++){
        Fake reset;reset.reset=n;
        expect(!run(reset,out),"reset during read rejected");
    }
    expect(signedRegister(0x8000)==-32768 && signedRegister(0xffff)==-1,"signed edges decoded");
    std::printf("{\"status\":\"PASS\",\"assertions\":%d,\"scope\":\"INA219 register decoder and injected transaction/reset failures\"}\n",checks);
}
