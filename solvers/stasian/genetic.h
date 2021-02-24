//
// Created by stast on 2/20/2021.
//

#ifndef SCHEDULE_GENETIC_H
#define SCHEDULE_GENETIC_H

#include "requirements.h"
#include <algorithm>
#include <random>
#include <utility>

#include  <random>
#include  <iterator>

template<typename Iter, typename RandomGenerator>
Iter selectRandomly(Iter start, Iter end, RandomGenerator& g) {
    std::uniform_int_distribution<> dis(0, std::distance(start, end) - 1);
    std::advance(start, dis(g));
    return start;
}

template<typename Iter>
Iter selectRandomly(Iter start, Iter end) {
    static std::random_device rd;
    static std::mt19937 gen(rd());
    return selectRandomly(start, end, gen);
}

int selectRandomInt(int start, int end) {
    static std::random_device rd;
    static std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(start, end);
    return dis(gen);
}

int selectProbabilityPercent(int prob) {
    return selectRandomInt(0, 99) < prob;
}

struct Lesson {
    Group* group;
    Subject* subject;
    Teacher* teacher;
    Auditorium* auditorium;

    int day;
    int num;

    bool operator< (const Lesson& other) const {
        if (this->day != other.day) {
            return this->day < other.day;
        }
        if (this->group->id != other.group->id) {
            return this->group->id < other.group->id;
        }
        return this->num < other.num;
    }
};

class Schedule {
    std::vector<Lesson> lessons;
    mutable int computedScore;
    Requirements* requirements;

public:
    explicit Schedule(Requirements* _requirements) : computedScore(-1), requirements(_requirements) {}
    explicit Schedule() : computedScore(-1), requirements(nullptr) {};
    void Normalize() {
        std::sort(lessons.begin(), lessons.end());
    }
    int GetScore() const {
        if (computedScore != -1) {
            return computedScore;
        }
        int score = 0;
        for (int i = 0; i < lessons.size(); i++) {
            if (lessons[i].subject->type == LECTURE && lessons[i].auditorium->type == PRACTICE) {
                score += 1;
            }
            for (int j = 0; j < i; j++) {
                if (lessons[j].day == lessons[i].day && lessons[j].num == lessons[i].num) {
                    if (lessons[j].teacher == lessons[i].teacher) {
                        score += 1;
                    }
                    if (lessons[j].group == lessons[i].group) {
                        score += 1;
                    }
                    if (lessons[j].auditorium == lessons[i].auditorium) {
                        score += 1;
                    }
                }
            }
        }
        return computedScore = score;
    }

    bool operator< (const Schedule& other) const{
        return this->GetScore() < other.GetScore();
    }

    static std::vector<Schedule> CreateInitialPopulation(int populationSize, Requirements* requirements) {
        std::vector<Schedule> population;
        for (int i = 0; i < populationSize; i++) {
            Schedule schedule(requirements);
            for (const auto& groupSubjectsArray : requirements->groupSubjects) {
                auto group = groupSubjectsArray.first;
                auto subjects = groupSubjectsArray.second;
                for (auto subject : subjects) {
                    auto teacher = *selectRandomly(requirements->subjectTeachers[subject].begin(),
                                                   requirements->subjectTeachers[subject].end());
                    auto auditorium = selectRandomly(requirements->auditoriums.begin(),
                                                     requirements->auditoriums.end())->second;
                    auto day = selectRandomInt(0, 4);
                    auto lessonNum = selectRandomInt(0, 3);
                    schedule.lessons.push_back(Lesson{group, subject, teacher, auditorium, day, lessonNum});
                }
            }
            population.push_back(schedule);
        }
        std::sort(population.begin(), population.end());
        return population;
    }

    Schedule Mutation(bool& goodMutation) {
        Schedule schedule(requirements);
        for (auto lesson : this->lessons) {
            if (selectProbabilityPercent(15)) {
                auto group = lesson.group;
                auto subject = lesson.subject;
                auto teacher = lesson.teacher;
                if (selectProbabilityPercent(40)) {
                    teacher = *selectRandomly(requirements->subjectTeachers[subject].begin(),
                                              requirements->subjectTeachers[subject].end());
                }
                auto auditorium = lesson.auditorium;
                if (selectProbabilityPercent(40)) {
                    auditorium = selectRandomly(requirements->auditoriums.begin(),
                                                requirements->auditoriums.end())->second;
                }
                auto day = lesson.day;
                if (selectProbabilityPercent(40)) {
                    day = selectRandomInt(0, 4);
                }
                auto lessonNum = lesson.num;
                if (selectProbabilityPercent(40)) {
                    lessonNum = selectRandomInt(0, 3);
                }
                schedule.lessons.push_back(Lesson{group, subject, teacher, auditorium, day, lessonNum});
            } else {
                schedule.lessons.push_back(lesson);
            }
        }
        goodMutation = true;
        if (schedule.GetScore() == this->GetScore()) {
            goodMutation = false;
        }
        return schedule;
    }

    Schedule CrossingOver(Schedule& other, bool& goodChild) {
        if (selectProbabilityPercent(90)) {
            goodChild = false;
            return Schedule(requirements);
        }
        std::map<std::pair<Group*, Subject*>, int> otherPos;
        Schedule schedule(requirements);
        for (auto lesson : this->lessons) {
            int pos = otherPos[{lesson.group, lesson.subject}];
            while (other.lessons[pos].group != lesson.group || other.lessons[pos].subject != lesson.subject) {
                pos++;
            }

            if (selectProbabilityPercent(70)) {
                schedule.lessons.push_back(lesson);
            } else {
                schedule.lessons.push_back(other.lessons[pos]);
            }

            otherPos[{lesson.group, lesson.subject}] = pos + 1;
        }
        goodChild = true;
        if (schedule.GetScore() == this->GetScore() || schedule.GetScore() == other.GetScore()) {
            goodChild = false;
        }
        return schedule;
    }

    void PrintSelf(const std::string& outputFile) const {
        printf("SCHEDULE\n==============\n");
        for (auto lesson : this->lessons) {
            printf("%d %d %d %d %d %d\n", lesson.subject->id, lesson.teacher->id,
                    lesson.group->id, lesson.auditorium->id, lesson.day, lesson.num);
        }

        if (!outputFile.empty()) {
            std::ofstream out(outputFile, std::ofstream::out);
            out << this->lessons.size() << "\n";
            for (auto lesson : this->lessons) {
                out << lesson.subject->id << " " << lesson.teacher->id << " " << lesson.group->id << " "
                    << lesson.auditorium->id << " " << lesson.day << " " << lesson.num << "\n";
            }
            out.close();
        }
    }
};

struct LessonOrder {
    Group* group;
    Subject* subject;
    Teacher* teacher;
};

class OrderBasedSchedule {
    mutable std::vector<LessonOrder> lessonOrder;
    mutable std::map<std::pair<int, int>, std::vector<Lesson>> lessons;
    mutable int computedScore;
    Requirements* requirements;
public:
    explicit OrderBasedSchedule(Requirements* _requirements) : computedScore(-1), requirements(_requirements) {};
    explicit OrderBasedSchedule() : computedScore(-1), requirements(nullptr) {};
    void Normalize() {}
    int GetScore() const {
        if (computedScore != -1) {
            return computedScore;
        }
        this->lessons.clear();
        int placedLessons = 0;
        for (auto orderedLesson : lessonOrder) {
            bool placedLesson = false;
            for (int day = 0; day < 5; day++) {
                for (int lessonNum = 0; lessonNum < 4; lessonNum++) {
                    std::set<Auditorium *> usedAuditoriums;
                    bool possiblePlace = true;
                    for (auto lesson : lessons[{day, lessonNum}]) {
                        if (lesson.group == orderedLesson.group || lesson.teacher == orderedLesson.teacher) {
                            possiblePlace = false;
                            break;
                        }
                        usedAuditoriums.insert(lesson.auditorium);
                    }
                    Auditorium *foundAuditorium = nullptr;
                    if (orderedLesson.subject->type == PRACTICE) {
                        for (auto auditorium : requirements->auditoriums) {
                            if (auditorium.second->type == PRACTICE &&
                                usedAuditoriums.find(auditorium.second) == usedAuditoriums.end()) {
                                foundAuditorium = auditorium.second;
                                break;
                            }
                        }
                    }
                    if (foundAuditorium == nullptr) {
                        for (auto auditorium : requirements->auditoriums) {
                            if (auditorium.second->type == LECTURE &&
                                usedAuditoriums.find(auditorium.second) == usedAuditoriums.end()) {
                                foundAuditorium = auditorium.second;
                                break;
                            }
                        }
                    }
                    if (possiblePlace && foundAuditorium) {
                        lessons[{day, lessonNum}].push_back(Lesson{orderedLesson.group, orderedLesson.subject,
                                                                   orderedLesson.teacher, foundAuditorium,
                                                                   day, lessonNum});
                        placedLesson = true;
                        placedLessons++;
                        break;
                    }
                }
                if (placedLesson) { break; }
            }
        }
        return computedScore = (requirements->lessonsCount - placedLessons);
    }

    bool operator< (const OrderBasedSchedule& other) const{
        return this->GetScore() < other.GetScore();
    }

    static std::vector<OrderBasedSchedule> CreateInitialPopulation(int populationSize, Requirements* requirements) {
        static std::random_device rd;
        static std::mt19937 gen(rd());

        std::vector<OrderBasedSchedule> population;
        std::vector<std::pair<Group*, Subject*>> groupSubjectArray;
        for (const auto& groupSubjectSubarray : requirements->groupSubjects) {
            for (auto groupSubject : groupSubjectSubarray.second) {
                groupSubjectArray.emplace_back(groupSubjectSubarray.first, groupSubject);
            }
        }
        for (int i = 0; i < populationSize; i++) {
            OrderBasedSchedule schedule(requirements);
            std::shuffle(groupSubjectArray.begin(), groupSubjectArray.end(), gen);
            for (auto groupSubject : groupSubjectArray) {
                auto teacher = *selectRandomly(requirements->subjectTeachers[groupSubject.second].begin(),
                                               requirements->subjectTeachers[groupSubject.second].end());
                schedule.lessonOrder.push_back(LessonOrder{groupSubject.first, groupSubject.second, teacher});
            }
            population.push_back(schedule);
        }
        std::sort(population.begin(), population.end());
        return population;
    }

    OrderBasedSchedule Mutation(bool& goodMutation) {
        OrderBasedSchedule mutated = *this;
        mutated.computedScore = -1;
        if (selectProbabilityPercent(75)) {
            do {
                int i = selectRandomInt(0, (int) mutated.lessonOrder.size() - 1);
                int j = selectRandomInt(0, (int) mutated.lessonOrder.size() - 1);
                std::swap(mutated.lessonOrder[i], mutated.lessonOrder[j]);
            } while (selectProbabilityPercent(35));
        }
        if (selectProbabilityPercent(75)) {
            bool changed = false;
            int noChangeTries = 0;
            do {
                int i = selectRandomInt(0, (int) mutated.lessonOrder.size() - 1);
                auto teacher = *selectRandomly(requirements->subjectTeachers[mutated.lessonOrder[i].subject].begin(),
                                               requirements->subjectTeachers[mutated.lessonOrder[i].subject].end());
                if (teacher != mutated.lessonOrder[i].teacher) {
                    changed = true;
                    mutated.lessonOrder[i].teacher = teacher;
                } else {
                    noChangeTries++;
                }
            } while ((!changed && noChangeTries < 25) || selectProbabilityPercent(50));
        }
        goodMutation = true;
        if (mutated.GetScore() == this->GetScore()) {
            goodMutation = false;
        }
        return mutated;
    }

    OrderBasedSchedule CrossingOver(OrderBasedSchedule& other, bool& goodChild) {
        if (selectProbabilityPercent(90)) {
            goodChild = false;
            return OrderBasedSchedule(requirements);
        }
        OrderBasedSchedule child(requirements);
        std::map<std::pair<Group*, Subject*>, int> groupSubjectCountSelf, groupSubjectCountOther;
        int posSelf = 0, posOther = 0;
        while (posSelf < this->lessonOrder.size() || posOther < other.lessonOrder.size()) {
            if (posSelf == this->lessonOrder.size() || (posOther != other.lessonOrder.size() && selectProbabilityPercent(80))) {

                while (groupSubjectCountSelf[{other.lessonOrder[posOther].group, other.lessonOrder[posOther].subject}] >
                       groupSubjectCountOther[{other.lessonOrder[posOther].group, other.lessonOrder[posOther].subject}]) {
                    posOther++;
                    if (posOther == other.lessonOrder.size()) {
                        break;
                    }
                }
                if (posOther == other.lessonOrder.size()) {
                    continue;
                }
                child.lessonOrder.push_back(other.lessonOrder[posOther]);
                groupSubjectCountOther[{other.lessonOrder[posOther].group, other.lessonOrder[posOther].subject}]++;
                posOther++;
            } else {
                while (groupSubjectCountOther[{this->lessonOrder[posSelf].group, this->lessonOrder[posSelf].subject}] >
                       groupSubjectCountSelf[{this->lessonOrder[posSelf].group, this->lessonOrder[posSelf].subject}]) {
                    posSelf++;
                    if (posSelf == this->lessonOrder.size()) {
                        break;
                    }
                }
                if (posSelf == this->lessonOrder.size()) {
                    continue;
                }
                child.lessonOrder.push_back(this->lessonOrder[posSelf]);
                groupSubjectCountSelf[{this->lessonOrder[posSelf].group, this->lessonOrder[posSelf].subject}]++;
                posSelf++;
            }
        }
        goodChild = true;
        if (child.GetScore() == this->GetScore() || child.GetScore() == other.GetScore()) {
            goodChild = false;
        }
        return child;
    }

    void PrintSelf(const std::string& outputFile) const {
        int lessonsCount = 0;
        printf("SCHEDULE\n==============\n");
        for (auto lessonDesc : this->lessons) {
            std::sort(lessonDesc.second.begin(), lessonDesc.second.end());
            for (auto lesson : lessonDesc.second) {
                lessonsCount++;
                printf("%d %d %d %d %d %d\n", lesson.subject->id, lesson.teacher->id,
                       lesson.group->id, lesson.auditorium->id, lesson.day, lesson.num);
            }
        }

        if (!outputFile.empty()) {
            std::ofstream out(outputFile, std::ofstream::out);
            out << lessonsCount << "\n";
            for (auto lessonDesc : this->lessons) {
                std::sort(lessonDesc.second.begin(), lessonDesc.second.end());
                for (auto lesson : lessonDesc.second) {
                    out << lesson.subject->id << " " << lesson.teacher->id << " " << lesson.group->id << " "
                        << lesson.auditorium->id << " " << lesson.day << " " << lesson.num << "\n";
                }
            }
            out.close();
        }
    }
};

template <class T>
class ScheduleGeneticRunner {
    std::vector<T> population;
    Requirements requirements;

    void PrintEpochScores(int epoch) {
        printf("EPOCH %d\n================\n", epoch);
        for (auto &schedule : population) {
            printf("%d ", schedule.GetScore());
        }
        printf("\n");
    }
public:
    explicit ScheduleGeneticRunner(Requirements _requirements) : requirements(std::move(_requirements)) {}

    void Run(int generationCount = 100, int populationSize = 100) {
        population = T::CreateInitialPopulation(populationSize, &requirements);
        PrintEpochScores(0);
        for (int epoch = 0; epoch < generationCount; epoch++) {
            std::vector<T> nextPopulation;
            for (int i = 0; i < population.size(); i++) {
                nextPopulation.push_back(population[i]);
                bool goodMutation;
                T mutation = population[i].Mutation(goodMutation);
                if (goodMutation) {
                    mutation.Normalize();
                    nextPopulation.push_back(mutation);
                }
                for (int j = 0; j < i; j++) {
                    bool goodChild;
                    T child = population[j].CrossingOver(population[i], goodChild);
                    if (goodChild) {
                        child.Normalize();
                        nextPopulation.push_back(child);
                    }
                }
            }
            population.clear();
            std::random_shuffle(nextPopulation.begin(), nextPopulation.end());
            std::sort(nextPopulation.begin(), nextPopulation.end());
            for (int i = 0, curCnt = 0; i < nextPopulation.size(); i++) {
                if (i == 0 || nextPopulation[i].GetScore() != nextPopulation[i-1].GetScore()) {
                    curCnt = 0;
                }
                curCnt++;
                if (curCnt < 10) {
                    population.push_back(nextPopulation[i]);
                }
            }
            if (population.size() > populationSize) {
                population.resize(populationSize);
            }
            PrintEpochScores(epoch + 1);
            if (population[0].GetScore() == 0) {
                break;
            }
        }
        population[0].PrintSelf(requirements.outputFile);
    }
};

#endif //SCHEDULE_GENETIC_H
