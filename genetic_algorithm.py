import random
import tsplib95
from typing import List
from numpy.random import default_rng
from itertools import chain
import math

from Chromosome import Chromosome
import numpy as np

CROSSOVER_MUTATION_PROB = 0.1
P_TOWER_MUTATION = 0.3
P_INVERSE_MUTATION = 0.3
P_ROTATION_TO_THE_RIGHT_MUTATION = 0.4

P_RANK_SELECTION = 0.2
P_ROULETTE_SELECTION = 0.8

P_ORDER_CROSSOVER = 0.4
P_PARTIALLY_MAPPED_CROSSOVER = 0.3
P_TWO_POINT_PARTIALLY_MAPPED_CROSSOVER = 0.3

NON_IMPROVING_GENERATIONS_BEFORE_STOP = 20


class GeneticAlgorithm:

    def __init__(self, problem, population_size=200, mutation_rate=0.3, elitism=0.2,crossover_rate = 1, selection_method=0, crossover_method=0, mutation_method=0):
        """
        Initialize the algorithm.
        :param problem: TSP problem to be solved
        :param population_size: size of population on each step
        :param mutation_rate: how many new children will come from mutation
        :param elitism: ratio of individuals surviving after each generation
        """

        self.rng = default_rng()
        self.population_size = population_size
        self.problem = problem
        self.mutation_rate = mutation_rate
        self.surviving = int(elitism * population_size)
        self.selection_method = self.select_selection(selection_method)
        self.crossover_method = self.select_crossover(crossover_method)
        self.mutation_method = self.select_mutation(mutation_method)
        self.crossover_rate = crossover_rate

        # Crossover can generate only an even number of new individuals. Here we ensure that after some individuals survived,
        # only an even number will have to eb generated by crossover
        if (population_size - self.surviving) % 2 == 1:
            self.surviving += 1
        self.all_populations = []
        self.current_population = None
        self.ranked_probabilities = [x / ((1 + population_size) / 2 * population_size) for x in
                                     reversed(range(1, population_size + 1))]
        self.fitness_probabilities = None
        self.min_distances = []

    def select_selection(self, index_for_selection):
        self.selection_functions = {
            0 : self.roulette_selection,
            1: self.rank_selection
        }

        return self.selection_functions[index_for_selection]
    
    def select_crossover(self, index_for_crossover):
        self.crossover_function = {
            0: self.one_point_partially_mapped_crossover,
            1: self.two_point_partially_mapped_crossover,
            2: self.order_crossover,
            3: self.cyclic_crossover
        }
        return self.crossover_function[index_for_crossover]
    
    def select_mutation(self, index_for_mutation):
        self.mutation_function = {
            0: self.tower_mutation,
            1: self.inversion_mutation,
            2: self.rotation_to_the_right_mutation,
            3: self.thrors_mutation
        }
        return self.mutation_function[index_for_mutation]


    def create_initial_population(self):
        # requirement:
        # Todo: I think we not have to consider asymetric graphs, for example where there is no route between cities or there different distances for (c1,c2), (c2,c1)
        # i think it makes sense that each individual has to be only once in their, therefore when we have a population of 100, with 100 differenct chromosomes
        # the start and the ende node has to be the origin city for each chromosome
        nodes = list(self.problem.get_nodes())
        population = []
        for i in range(self.population_size):
            while True:
                new_list = nodes.copy()
                random.shuffle(new_list)
                if new_list not in population:
                    break

            population.append(Chromosome(new_list, self.problem))
        return population

    def use_genetic_algorithm(self, max_generations=1000):
        # create initial population
        self.current_population = self.create_initial_population()
        self.current_population = sorted(self.current_population, key=lambda chrom: -chrom.fitness)
        self.recalculate_fitness_probabilities()
        self.all_populations.append(self.current_population)
        # TODO: add distance of initial population
        best_distance = float("inf")
        non_improving_generations = 0

        for generation in range(max_generations):

            new_population = self.perform_selection_crossover()
            self.perform_mutations(new_population)
            # The number of best parents automatically go to the next population
            new_population += self.current_population[:self.surviving]
            self.all_populations.append(new_population.copy())
            self.current_population = new_population
            self.current_population.sort(key=lambda chrom: -chrom.fitness)
            self.recalculate_fitness_probabilities()

            # best_generation_distance = min(c.get_distance() for c in self.current_population)
            best_generation_distance = self.current_population[0].get_distance()
            self.min_distances.append(best_generation_distance)
            if best_generation_distance < best_distance:
                best_distance = best_generation_distance
                non_improving_generations = 0
                print(f"Generation {generation}. New best distance: {best_distance}")
            else:
                non_improving_generations += 1

            if non_improving_generations > NON_IMPROVING_GENERATIONS_BEFORE_STOP:
                print(f"Stopping on generation {generation} because of no improvement")
                return
        print("Reached max number of generations")

    def perform_selection_crossover(self) -> List[Chromosome]:
        """
        Perform the crossover for all 
        :return: List of chromosomes created by a crossover
        """
        children = []
        for i in range((self.population_size - self.surviving) // 2):
            chr1,chr2 = self.selection_method(2)
            if random.random() > self.crossover_rate:
                children.append(chr1)
                children.append(chr2)
                continue
            children += self.crossover_method(chr1, chr2)
            
        return children


    def perform_mutations(self, population) -> None:
        """
        Perform mutations on the given population (inplace by modifying the original list)
        :param population: Population to be mutated
        """
        for i in range(len(population)):
            # Mutate an individual with the certain probability
            if random.random() > self.mutation_rate:
                continue

            self.mutation_method(population[i])
            population[i].update_fitness()

    def recalculate_fitness_probabilities(self) -> None:
        """
        The probabilities of each individual to be selected in ranked selection are calculated here only once for each
        population to avoid extra computations.
        Recalculating probabilities based on fitness of individuals
        """
        # to ensure all fitnesses are up todate
        for c in self.current_population:
            c.update_fitness()

        fitnesses = [c.fitness for c in self.current_population]
        # Very often the fitness here are very low as path lengths are far from zero
        # (e.g. path lengths of 3100 and 3000) would lead to almost the same probabilities for these individuals
        # To avoid this, we rescale the fitness by subtracting the minimum one form each
        s = sum(fitnesses) - min(fitnesses) * len(fitnesses)
        self.fitness_probabilities = [(fitness - min(fitnesses)) / s for fitness in fitnesses]

    def print_population(self, population):
        for c in population:
            print(c.get_as_tuple())

    def evolution_of_minimum(self):
        return self.min_distances

    # requirements for selection:
    # large fitness large probablity to get selected
    # not too much pressure, so that the space ge's more explored
    def roulette_selection(self, count=1):
        # requirements:
        # select probabilites after fitness of chromosome
        # non negative fitness

        # choose one regarding probabilities
        return list(np.random.choice(self.current_population, count, p=self.fitness_probabilities))

    def rank_selection(self, count=1):
        # requirements
        # Assign ranks by sorting individuals by increasing fitness
        # Probability of selection proportional to rank

        return list(np.random.choice(self.current_population, count, p=self.ranked_probabilities))

    def one_point_partially_mapped_crossover(self, first_chromosome, second_chromosome):
        # requirements
        # Divide both chromosomes at a random position
        # swap first half of values

        # we want to enforce that two new chromosomes are generated and not that the old ones are coppied
        position = np.random.randint(low=1, high=len(first_chromosome.route) - 1)

        new_first_route = first_chromosome.route.copy()
        new_second_route = second_chromosome.route.copy()
        # switch cities in poisition i for new routes from parent routes
        for i in range(position):

            # if element is not already at the same place
            if new_first_route[i] != second_chromosome.route[i]:
                firstroute_index_for_current_element = new_first_route.index(second_chromosome.route[i])
                # put element to replace on the index where element which replaces is
                new_first_route[firstroute_index_for_current_element] = new_first_route[i]
                # replace 
                new_first_route[i] = second_chromosome.route[i]

            # same for b
            secondroute_index_for_current_element = new_second_route.index(first_chromosome.route[i])
            if i != secondroute_index_for_current_element:
                new_second_route[secondroute_index_for_current_element] = new_second_route[i]
                new_second_route[i] = first_chromosome.route[i]

        # create two new chromosomes with route
        first = Chromosome(new_first_route, self.problem)
        second = Chromosome(new_second_route, self.problem)

        return [first, second]

    def two_point_partially_mapped_crossover(self, first_chromosome: Chromosome, second_chromosome: Chromosome):
        def generate_offspring(parent_main: Chromosome, parent_secondary: Chromosome, pos1, pos2):
            offspring = Chromosome(parent_main.route.copy(), self.problem)

            for i in chain(range(0, pos1), range(pos2, len(parent_main.route))):
                candidate = parent_secondary.route[i]
                # Search for the replacement while the candidate is in the cut chunk
                while candidate in parent_main.route[p1:p2]:
                    candidate = parent_secondary.route[parent_main.route.index(candidate)]
                offspring.route[i] = candidate
            offspring.update_fitness()
            return offspring

        p1, p2 = np.sort(self.rng.choice(len(first_chromosome.route), size=2, replace=False))

        return generate_offspring(first_chromosome, second_chromosome, p1, p2), generate_offspring(second_chromosome,
                                                                                                   first_chromosome, p1,
                                                                                                   p2)

    def order_crossover(self, first_chromosome: Chromosome, second_chromosome: Chromosome):
        def order_chromosome_create_child(parent_main: Chromosome, parent_secondary: Chromosome, pos1,
                                          pos2) -> Chromosome:
            # Create a child chromosome with the same route as the main parent
            child = Chromosome(parent_main.route.copy(), parent_main.problem)

            # We keep the part of the chromosome between the two selected positions,
            # but nodes on all the replace_indices will be reordered
            replace_indices = list(range(pos1, pos2)) if pos2 > pos1 else list(range(0, pos2)) + list(
                range(pos1, len(parent_main.route)))

            # Select specific nodes that will be reordered into a set
            nodes_to_reorder = {parent_main.route[i] for i in replace_indices}

            # Nodes in the child chromosome are ordered with respect to their order in the secondary parent chromosome
            # but starting from the end of the selected chunk
            # Reorder the nodes_to_reorder into the same order as in the secondary chromosome
            nodes_ordered = [parent_secondary.route[i] for i in
                             chain(range(pos1, len(parent_main.route)), range(0, pos1)) if
                             parent_secondary.route[i] in nodes_to_reorder]

            for i in range(len(replace_indices)):
                child.route[replace_indices[i]] = nodes_ordered[i]
            child.update_fitness()
            return child

        p1, p2 = self.rng.choice(len(first_chromosome.route), size=2, replace=False)
        return order_chromosome_create_child(first_chromosome, second_chromosome, p1, p2), \
            order_chromosome_create_child(second_chromosome, first_chromosome, p1, p2),

    def cyclic_crossover(self,first_chromosome: Chromosome, second_chromosome: Chromosome):
        def cyclic_crossover_create_child(parent_main: Chromosome, parent_secondary: Chromosome):
            # we start cycle with the first position of parent_main
            route_main = parent_main.route.copy()
            route_second = parent_secondary.route.copy()
            child_route = parent_main.route.copy()
            
            # creating the cycle
            position = 0
            cycle = []
            while True:
                cycle.append(route_main[position])
                if route_second[position] is not route_main[0]:
                    position = route_main.index(route_second[position])
                else:
                    break
            #take only the elments at the exact same position of secondary_route, which are not in the cycle
            for i in range(len(route_second)):
                if route_second[i] not in cycle:
                    child_route[i] = route_second[i]
            
            return Chromosome(child_route, self.problem)
        children = []
        children.append(cyclic_crossover_create_child(first_chromosome,second_chromosome))
        children.append(cyclic_crossover_create_child(second_chromosome, first_chromosome))
        return children
    

    @staticmethod
    def tower_mutation(chrom):
        positions = random.sample(range(len(chrom.route)), 2)
        chrom.route_swap_positions(positions[0], positions[1])

    @staticmethod
    def inversion_mutation(chrom):
        p1, p2 = random.sample(range(len(chrom.route)), 2)
        # Here the route is a "cyclic" array, so the first index goes after the last one
        # When performing inverse it's important to not prioritize inverses in the center of array over ones
        # on the edges
        if p1 < p2:
            # A normal inverse in the middle of a chromosome
            chrom.route[p1:p2] = chrom.route[p1:p2][::-1]
        else:
            # The segment that need to be inverse goes "over the edge" of the array
            # I use the property of array being cyclic to perform the inverse

            # Firstly, inverse the middle part
            chrom.route[p2:p1] = chrom.route[p2:p1][::-1]
            # Then, inverse the whole route to keep the middle part back in initial order
            chrom.route = chrom.route[::-1]

    @staticmethod
    def rotation_to_the_right_mutation(chrom):
        shift_right = lambda arr, n: arr[len(arr) - n:] + arr[:len(arr) - n]
        p1, p2 = random.sample(range(len(chrom.route)), 2)
        if p1 < p2:
            k = random.randint(1, p2 - p1)
            chrom.route[p1:p2] = shift_right(chrom.route[p1:p2], k)
        else:
            # If the chosen chunk goes "over" the edge
            # Perform a simple shift of the whole array that does not influence the solution
            chrom.route = chrom.route[p2:] + chrom.route[:p2]
            shift_chunk_size = len(chrom.route) - (p1 - p2)
            k = random.randint(1, shift_chunk_size)
            chrom.route[0:shift_chunk_size] = shift_right(chrom.route[0:shift_chunk_size], k)
            # Perform the shift back to the left to keep the not altered part on the same place
            chrom.route = chrom.route[len(chrom.route) - p2:] + chrom.route[:len(chrom.route) - p2]
        
    def thrors_mutation(self,chrom):
        # take randomly three position i >j>l, has not to be successive elements
        # change j with i, l with  j, and i with l
        new_route = chrom.route.copy()
        positions = random.sample(chrom.route, 3)
        positions.sort()

        for i in range(len(positions)):
            place_from = (i + len(positions) - 1) % len(positions)
            new_route[positions[i]] = chrom.route[positions[place_from]]
    
        chrom.set_route(new_route)
        
        

if __name__ == '__main__':
    problem = tsplib95.load('datasets/gr17.tsp.txt')
    Alg = GeneticAlgorithm(problem, 200,0.3,0.2,1,1,3,3)

    # test_cyclic_crossover = Alg.create_initial_population()
    # Alg.print_population([test_cyclic_crossover[0]])
    # Alg.print_population(Alg.cyclic_crossover(test_cyclic_crossover[0],test_cyclic_crossover[1]))
    

    print(Alg.use_genetic_algorithm(1000))
    for pop in Alg.all_populations:
        print("new population")
        Alg.print_population(pop)

    #a = [5,7,1,3,6,4,2]
    #b = [4,6,2,7,3,1,5]
    
    print(Alg.evolution_of_minimum())
