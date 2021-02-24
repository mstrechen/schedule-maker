//
// Created by stast on 2/20/2021.
//

#ifndef SCHEDULE_REQUIREMENTS_H
#define SCHEDULE_REQUIREMENTS_H

#include <string>
#include <map>
#include <set>
#include <utility>
#include <vector>
#include <fstream>

#define LECTURE 0
#define PRACTICE 1

struct Teacher {
    int id;
    explicit Teacher(int _id) : id(_id) {}
    bool operator<(const Teacher& other) const { return this->id < other.id; }
};

struct Subject {
    int id;
    int type;
    Subject(int _id, int _type) : id(_id), type(_type) {}
    bool operator<(const Subject& other) const { return this->id < other.id; }
};

struct Auditorium {
    int type;
    int id;
    Auditorium(int _id, int _type) : id(_id), type(_type) {}
    bool operator<(const Auditorium& other) const { return this->id < other.id; }
};

struct Group {
    int id;
    explicit Group(int _id) : id(_id) {}
    bool operator<(const Group& other) const { return this->id < other.id; }
};

struct Requirements {
    std::map<int, Teacher*> teachers;
    std::map<int, Subject*> subjects;
    std::map<int, Auditorium*> auditoriums;
    std::map<int, Group*> groups;
    std::map<Subject*, std::vector<Teacher*>> subjectTeachers;
    std::map<Group*, std::vector<Subject*>> groupSubjects;
    std::string outputFile;
    int lessonsCount;

    void Init(const std::string& filepath, const std::string& outputPath) {
        this->outputFile = outputPath;
        std::ifstream input(filepath, std::ifstream::in);

        int groupCount, teacherCount, subjectCount, lectureSubjectsCount, auditoriumCount, lectureAuditoriumCount;
        input >> groupCount >> teacherCount >> subjectCount >> lectureSubjectsCount >> auditoriumCount >> lectureAuditoriumCount;
        for (int i = 0; i < groupCount; i++) {
            groups[i] = new Group(i);
        }
        for (int i = 0; i < teacherCount; i++) {
            teachers[i] = new Teacher(i);
        }
        for (int i = 0; i < subjectCount; i++) {
            subjects[i] = new Subject(i, (i < lectureSubjectsCount ? LECTURE : PRACTICE));
        }
        for (int i = 0; i < auditoriumCount; i++) {
            auditoriums[i] = new Auditorium(i, (i < lectureAuditoriumCount ? LECTURE : PRACTICE));
        }

        int subjectTeachersCount;
        input >> subjectTeachersCount;
        for (int i = 0; i < subjectTeachersCount; i++) {
            int subjectId, teacherId;
            input >> subjectId >> teacherId;
            subjectTeachers[subjects[subjectId]].push_back(teachers[teacherId]);
        }

        int groupSubjectsCount;
        lessonsCount = 0;
        input >> groupSubjectsCount;
        for (int i = 0; i < groupSubjectsCount; i++) {
            int groupId, subjectId, cnt;
            input >> subjectId >> groupId >> cnt;
            for (int j = 0; j < cnt; j++) {
                groupSubjects[groups[groupId]].push_back(subjects[subjectId]);
                lessonsCount++;
            }
        }
    }
};


#endif //SCHEDULE_REQUIREMENTS_H
