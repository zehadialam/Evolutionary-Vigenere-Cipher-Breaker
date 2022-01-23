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

KEY_LENGTH = 16

POPULATION_SIZE = 75
MAX_GENERATIONS = 10000

plaintext = 'Physical Chemistry is the study of macroscopic, and particulate phenomena in chemical systems in terms of the principles, practices, and concepts of physics such as motion, energy, force, time, thermodynamics, quantum chemistry, statistical mechanics, analytical dynamics and chemical equilibria.'


def generate_random_letter():
    """Return random uppercase letter from the English alphabet"""
    return secrets.choice(string.ascii_uppercase)


ENCRYPTION_KEY = "".join([generate_random_letter() for _ in range(KEY_LENGTH)])


def format_ciphertext(the_ciphertext):
    """
    Return the formatted ciphertext.
    Formatted refers to conversion to uppercase letters and the removal of
    spaces and non-alphabetic characters (e.g. punctuation)
    """
    formatted_cipher_text = ''
    for c in the_ciphertext:
        if c.isalpha():
            formatted_cipher_text += c.upper()
    return formatted_cipher_text


def restore_original_format(original_format, modified_format):
    """
    Return the original ciphertext format with casing, spaces, and
    punctuation restored.
    """
    restored_text = ''
    i = 0
    for c in original_format:
        if c.isalpha():
            if c.isupper():
                restored_text += modified_format[i].upper()
            elif c.islower():
                restored_text += modified_format[i].lower()
            i += 1
        else:
            restored_text += c
    return restored_text


# encrypted message
CIPHERTEXT = restore_original_format(plaintext, Vigenere(ENCRYPTION_KEY).encipher(plaintext))

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
    decrypted = Vigenere(key).decipher(format_ciphertext(CIPHERTEXT))
    return (fitness.score(decrypted)),


# register fitness function with the toolbox
toolbox.register("evaluate", fitness_function)


# implements random reset mutation, since it is not part of DEAP
def mut_random_reset(individual, indpb):
    """Return an individual that has undergone random reset mutation"""
    for i in range(len(individual)):
        if random.random() < indpb:
            individual[i] = generate_random_letter()
    return individual,


# return true if the past 6 max fitnesses exist and are equal.
def terminate(max_fitness_values):
    """Return True if the past six max fitnesses exist and are equal"""
    N = 6
    # If there have been less than N generations then return false. 
    if len(max_fitness_values) < N:
        return False
    else:
        # Retrieve the most recent N values of max_fitness_values
        last_N_elements = max_fitness_values[-N:]
        # If statement to see if they are all equal
        if all(x == last_N_elements[0] for x in last_N_elements):
            # Ask the human in the loop to read the message
            print("Is the individual fully decrypted? Y or N?")
            user_input = input()
            if user_input == "Y".lower():
                return True
    return False


# register selection operator with the toolbox
toolbox.register("select", tools.selTournament, tournsize=3)
# register crossover operator with the toolbox
toolbox.register("mate", tools.cxUniform, indpb=0.7)
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
    while generation < MAX_GENERATIONS and not terminate(max_fitness_values):
        generation += 1
        # selects the individuals for the next generation (excluding elite individuals)
        offspring = toolbox.select(population, len(population))
        # selected individuals become offspring
        offspring = list(map(toolbox.clone, offspring))
        # crossover pairs of offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values
        # mutate offspring
        for mutant in offspring:
            toolbox.mutate(mutant)
            del mutant.fitness.values
        # calculate fitness for new individuals
        new_individuals = [ind for ind in offspring if not ind.fitness.valid]
        new_fitness_values = list(map(toolbox.evaluate, new_individuals))
        for individual, fitness_value in zip(new_individuals, new_fitness_values):
            individual.fitness.values = fitness_value
        # sort offspring by fitness values
        offspring = sorted(offspring, key=lambda x: x.fitness.values[0])
        # replace worst n offspring with the best n saved individuals (to implement elitism)
        offspring[:hof_size] = hof.items
        # Update the hall of fame with new best individuals
        hof.update(offspring)
        # replace current population with offspring:
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
        print("Best Individual =", *population[best_index])
        print(
            f'Decrypted message: {restore_original_format(CIPHERTEXT, Vigenere("".join(list(population[best_index]))).decipher(format_ciphertext(CIPHERTEXT)))} \n')
        if generation == MAX_GENERATIONS or "".join(population[best_index]) == ENCRYPTION_KEY:
            print(f'The encryption key is {ENCRYPTION_KEY}')
            if "".join(population[best_index]) == ENCRYPTION_KEY:
                print('The key was successfully cracked!')
            else:
                print('The key was not successfully cracked')

    # plot statistics
    sns.set_style("whitegrid")
    fig, ax = plt.subplots()
    plt.plot(max_fitness_values, color='red', label='Max fitness')
    plt.plot(mean_fitness_values, color='green', label='Mean fitness')
    ax.legend()
    plt.xlabel('Generation')
    plt.ylabel('Max / Mean Fitness')
    plt.title('Max and Mean Fitness over Generations')
    plt.show()


if __name__ == '__main__':
    main()
