import random


class GeneticAlgorithm:
    def __init__(self, initial_population, fitness_function, crossover, mutation, mutation_prob=0.15, epochs=50, goal=1e9, repro_rate=0.5):
        self.population = []
        for individual in initial_population:
            fitness = fitness_function(individual)
            self.population.append((individual, fitness))
        self.population_size = len(self.population)
        self.fitness_function = fitness_function
        self.mutation = mutation
        self.crossover = crossover
        self.epochs = epochs
        self.mutation_prob = mutation_prob
        self.goal = goal
        self.repro_rate = repro_rate

    # roulette wheel selection
    def select(self):
        def restore_individual(fitness):
            for i in range(len(fitnesses)):
                if fitnesses[i] > fitness:
                    return self.population[i]
            return self.population[-1]

        current_fitness = 0
        fitnesses = []
        for individual in self.population:
            current_fitness += individual[1]
            fitnesses.append(current_fitness)

        rand1 = random.randint(0, current_fitness - 1) if current_fitness else 0
        rand2 = random.randint(0, current_fitness - 1) if current_fitness else 0
        return restore_individual(rand1),  restore_individual(rand2)

    def fit(self):
        selections_per_epoch = int(self.population_size * self.repro_rate)
        mutations_per_epoch = int(self.population_size * self.mutation_prob)
        for epoch in range(self.epochs):
            if self.reached_goal():
                return

            for selection in range(selections_per_epoch):
                parent1, parent2 = self.select()
                offspring = self.crossover(parent1, parent2)
                fitness = self.fitness_function(offspring)
                self.population.append((offspring, fitness))

                for _ in range(mutations_per_epoch):
                    individual = self.population[random.randint(0, self.population_size - 1)][0]
                    mutant = self.mutation(individual)
                    if mutant is not None:
                        self.population.append((mutant, self.fitness_function(mutant)))

            self.finest_survival()

        return self.most_fit()[0]

    def finest_survival(self):
        sorted_population = sorted(self.population, key=lambda x: -x[1])
        self.population = sorted_population[0:self.population_size]

    def most_fit(self):
        best = self.population[0]

        for individual in self.population:
            if individual[1] > best[1]:
                best = individual

        return best

    def reached_goal(self):
        if self.most_fit()[1] >= self.goal:
            return True
        return False
