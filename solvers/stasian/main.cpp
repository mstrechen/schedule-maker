#include <iostream>
#include "requirements.h"
#include "genetic.h"

int main(int argc, char** argv) {
    Requirements requirements;
    requirements.Init("input.txt", "output.txt");
    if (argc > 1 && argv[1][0] == '1') {
        ScheduleGeneticRunner<OrderBasedSchedule> runner = ScheduleGeneticRunner<OrderBasedSchedule>(requirements);
        runner.Run(50, 4);
    } else {
        ScheduleGeneticRunner<Schedule> runner = ScheduleGeneticRunner<Schedule>(requirements);
        runner.Run();
    }
    return 0;
}
