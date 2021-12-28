# Vigenère Cipher Breaker using a Genetic Algorithm


## Genetic Algorithm

Genetic algorithms are a kind of search algorithm that seek to find solutions from a problem space by making use of the Darwinian principles of variation, inheritance, and selection. In the context of biological evo-lution, individuals within a population who harbor traits that are more fit for their environment are more likely to pass on those traits to the next generation, such that there is an increase in that trait in the population over time. Similarly, in genetic algorithms, individuals with good genes according to a fitness function can pass on those genes to the next generation, which can lead to convergence to a solution over successive generations.

Problems that are to be solved using a genetic algorithm must undergo the proper set up and formulation. In this project, the following constitutes the problem formulation:

<b><ins>Representation:</ins></b> Chromosomes consist of genes that are ASCII values 65 – 90 (i.e., uppercase characters of English alphabet).<br><br>
<ins>Initialization:</ins> Randomly generate population of 75 individuals.<br>
<ins>Fitness Function:</ins> The sum of the log probabilities of all quadgrams within a message decrypted with a candidate key.<br>
<ins>Mutation:</ins> Random resetting (i.e., character at random chromosomal position is replaced with a different character) with a probability of 1 / key length.<br>
<ins>Crossover:</ins> Uniform crossover with a probability of 0.7<br>
<ins>Selection:</ins> Ternary tournament selection<br>
<ins>Termination condition:</ins> Message is fully decrypted.<br>
