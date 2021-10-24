import matplotlib.pyplot as plt
import ngram_score as ns
import random
import secrets
import string
import seaborn as sns

from deap import base
from deap import creator
from deap import tools

from pycipher import Vigenere

KEY_LENGTH = 14

POPULATION_SIZE = 100
CROSSOVER_PROBABILITY = 0.9
MUTATION_PROBABILITY = 0.75
MAX_GENERATIONS = 30

# encrypted message with spaces and non-alphabetic characters (e.g. punctuation) removed
ciphertext = "HLAJMVPLUZAAZVLVAZWMWEKLQRPRXQCTVHHCGHEQRQVTCIXBRUDSPSGKWRQDIGPIFUDSDLUENJCLIEEKEBKHJQUFJMWEHJEBTLHPGJTKPCLAYSJDFHEFRVTPLKKTGKQWKTWLJCZSOAFWASPVRXGGQXKFTHLMOVXATREGZMEDEMEJUNPNLMIQYHEMUKVRHTSLEGKLUENDIVWAFAYGRQSPAKMVPLVQJODLUWCEHVWEEAYOCHIYKCMUGIS"


def generate_random_letter():
    """Return random uppercase letter from the English alphabet"""
    return secrets.choice(string.ascii_uppercase)


# using DEAP's Toolbox class to create genetic algorithm components
toolbox = base.Toolbox()
# indicates that the fitness is to be maximized
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
# creates the genes of a random individual in the initial population
toolbox.register("createrandomkey", generate_random_letter)
# defines the individual that composes the population. The individual is represented as a list of characters
creator.create("Individual", list, fitness=creator.FitnessMax)
# creates the individual by repeatedly calling the create_random_key() function until it is the size of the key length
toolbox.register("individualCreator", tools.initRepeat, creator.Individual, toolbox.createrandomkey, KEY_LENGTH)
# creates the population by repeatedly calling the individualCreator
toolbox.register("populationCreator", tools.initRepeat, list, toolbox.individualCreator)


def fitness_function(key):
    """Return a tuple of the numeric score given to a message decrypted with a key"""
    fitness = ns.ngram_score('quadgrams.txt')
    plaintext = Vigenere(key).decipher(ciphertext)
    return (fitness.score(plaintext)),


# register fitness function with the toolbox
toolbox.register("evaluate", fitness_function)


# implements random reset mutation, since it is not part of DEAP
def mut_random_reset(individual, indpb):
    """Return an individual that has undergone random reset mutation"""
    for i in range(len(individual)):
        if random.random() < indpb:
            individual[i] = generate_random_letter()
    return individual,


# register selection operator with the toolbox
toolbox.register("select", tools.selTournament, tournsize=3)
# register crossover operator with the toolbox
toolbox.register("mate", tools.cxUniform, indpb=1.0 / KEY_LENGTH)
# register mutation operator with the toolbox
toolbox.register("mutate", mut_random_reset, indpb=1.0 / KEY_LENGTH)


def main():
    """Run the genetic algorithm"""

    # create the initial population where generation = 0
    population = toolbox.populationCreator(n=POPULATION_SIZE)
    generation = 0
    # create hall of fame, which retains the best n individuals as specified
    hof = tools.HallOfFame(10)
    hof_size = len(hof.items)
    # calculate fitness for each individual in the population
    fitness_values = list(map(toolbox.evaluate, population))
    for individual, fitness_value in zip(population, fitness_values):
        individual.fitness.values = fitness_value
    # hold fitness statistics
    max_fitness_values = []
    mean_fitness_values = []
    # run genetic algorithm for specified generations
    while generation < MAX_GENERATIONS:
        generation += 1
        # selects the individuals for the next generation (excluding elite individuals)
        offspring = toolbox.select(population, len(population) - hof_size)
        # selected individuals become offspring
        offspring = list(map(toolbox.clone, offspring))
        # crossover pairs of offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CROSSOVER_PROBABILITY:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values
        # mutate offspring (with elite individuals excluded)
        for mutant in offspring:
            if random.random() < MUTATION_PROBABILITY:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        # calculate fitness for new individuals
        new_individuals = [ind for ind in offspring if not ind.fitness.valid]
        new_fitness_values = list(map(toolbox.evaluate, new_individuals))
        for individual, fitness_value in zip(new_individuals, new_fitness_values):
            individual.fitness.values = fitness_value
        # add the best n individuals back into the population (to implement elitism)
        offspring.extend(hof.items)
        # Update the hall of fame with new best individuals
        hof.update(offspring)
        # replace current population offspring:
        population[:] = offspring
        # gather and print fitness statistics for each generation
        fitness_values = [ind.fitness.values[0] for ind in population]
        max_fitness = max(fitness_values)
        mean_fitness = sum(fitness_values) / len(population)
        max_fitness_values.append(max_fitness)
        mean_fitness_values.append(mean_fitness)
        print(f'Generation: {generation} Max Fitness = {max_fitness}, Avg Fitness = {mean_fitness}')
        # print best individual:
        best_index = fitness_values.index(max(fitness_values))
        print("Best Individual = ", *population[best_index], "\n")

    # plot statistics
    sns.set_style("whitegrid")
    plt.plot(max_fitness_values, color='red')
    plt.plot(mean_fitness_values, color='green')
    plt.xlabel('Generation')
    plt.ylabel('Max / Average Fitness')
    plt.title('Max and Average Fitness over Generations')
    plt.show()


if __name__ == '__main__':
    main()
