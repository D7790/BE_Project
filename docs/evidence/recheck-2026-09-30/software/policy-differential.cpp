#include <iostream>
#include <iomanip>
#include "controller.h"
int main() {
    int n; std::cin >> n;
    std::cout << std::setprecision(14);
    for (int caseNo=0; caseNo<n; ++caseNo) {
        Controller c; double initial; int steps;
        std::cin >> initial >> steps; c.socPct=initial; c.optionalOn=true;
        for (int k=0; k<steps; ++k) {
            Sample s; float dt;
            std::cin >> dt >> s.batteryV >> s.batteryA >> s.loadW >> s.temperatureC >> c.minimumRuntimeH;
            s.valid=true; c.update(s, dt);
            std::cout << c.socPct << ' ' << c.energyWh << ' ' << c.runtimeH << ' '
                << c.noSolarRuntimeH << ' ' << c.optionalOn << ' ' << c.state << '\n';
        }
    }
}
