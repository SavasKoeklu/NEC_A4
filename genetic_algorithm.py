import random
import tsplib95
import pandas as pd
import numpy as np

class GeneticAlgorithm:

     # Todo: chnage name of activation function to "fact"
    def __init__(self, problem, initial_population_size=100):
        # the size of the initial population
        self.initial_population_size = initial_population_size
        self.problem = problem

        # create array where all populations are stored
        self.all_populations = []

    def create_initial_population(self):
        # requirement:
            # Todo: I think we not have to consider asymetric graphs, for example where there is no route between cities or there different distances for (c1,c2), (c2,c1)
            # i think it makes sense that each individual has to be only once in their, therefore when we have a population of 100, with 100 differenct chromosomes
            # the start and the ende node has to be the origin city for each chromosome
        nodes = list(self.problem.get_nodes())
        firstelement = nodes[0]
        nodes.remove(nodes[0])
        population = []
        for i in range(self.initial_population_size):
            while True:
                new_list = nodes.copy()
                random.shuffle(new_list)
                if new_list not in population:
                    break
            new_list.insert(0,firstelement)
            
            population.append(Chromosome(new_list,self.problem))
        return population
    
    def get_minimal_route(self):
        # create initial population
        
        initial_population =  self.create_initial_population()
        self.all_populations.append(initial_population)

        # TODO: find stationary state, so how much generations?
        for generation in range(1):
            select_one =  self.rank_selection(initial_population)
            select_two = self.rank_selection(initial_population)
            new_chromosomes = self.one_point_crossover(select_one,select_two)
            self.print_population([select_one, select_two])
            print("crossovered")
            self.print_population(new_chromosomes)
            
        

        
        


        return select_two
        # evaluate fitness function#
    
    def print_population(self,population):
        for c in population:
            print(c.get_as_tuple())

    #requirements for selection:
            #large fitness large probablity to get selected
            # not too much pressure, so that the space ge's more explored
    def roulette_selection(self,population):
        #requirements:
            #select probabilites after fitness of chromosome
            # non negative fitness
        
        # calculate fitness for all chromosomes
        fitnesses = [ c.fitness  for c in population ]
        # calculate probabilites for all chromosomes
        probablities = [fitness/sum(fitnesses) for fitness in fitnesses]
        # choose one regarding probablities
        selected_one_index = np.random.choice(len(population),1,p=probablities)[0]
        return population[selected_one_index]
    
    def rank_selection(self, population):
        #requirements
            # Assign ranks by sorting individuals by increasing fitness
            # Probability of selection proportional to rank

        # sort after first fitness
        res = sorted(population, key = lambda x: x.fitness)
        # calculate probablities
        probablities = [(res.index(chromosome)+1)/sum(range(1,len(population)+1)) for chromosome in res]
        selected_one_index = np.random.choice(len(population),1,p=probablities)[0]

        return res[selected_one_index]
    
    def one_point_crossover(self, first_chromosome, second_chromosome):
        #requirements
            #Divide both chromosomes at a random position
            #Swap the second half of the chromosomes
        
        # starts at one becuase to enforce at least that one element is crossed over
        position =  np.random.randint(low=1,high=len(first_chromosome.route)-1)
        
        new_first_route = first_chromosome.route.copy()
        new_second_route = second_chromosome.route.copy()

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
        first = Chromosome(new_first_route,self.problem)
        second = Chromosome(new_second_route, self.problem)

        print(f"position for crossover:{position}")

        return [first,second]


        
        
        

    
    

class Chromosome:

    def __init__(self, route, problem):
        self.route = route
        self.problem = problem
        self.fitness = self.fitness_for_route(route)

    def fitness_for_route(self,route):
    # requirements fitness function to maximize when the distance of the route minimizes
        fitness = 1/float(self.problem.trace_tours([route])[0])
        return fitness
    
    def set_route(self,route):
        self.route = route
        self.fitness = self.fitness_for_route(route)
    
    def get_as_tuple(self):
        return (self.route, self.fitness)
    
    

    

    

        


problem = tsplib95.load('datasets/gr17.tsp.txt')
Alg = GeneticAlgorithm(problem,2)

Alg.get_minimal_route().get_as_tuple()
    
# a = [5,7,1,3,6,4,2]
# b = [4,6,2,7,3,1,5]
# position = np.random.randint(low=1,high=(len(a)-1))
# # switch the first half
# new_a = a.copy()
# new_b = b.copy()
# print(f"position: {position}")


# for i in range(position):
#     a_index_for_current_element = new_a.index(b[i])
#     # if element is not already at the same place
#     if new_a[i] != b[i]:
#         # put element to replace on the index where element which replaces is
#         new_a[a_index_for_current_element] = new_a[i]
#         # replace 
#         new_a[i] = b[i]

#     # same for b
#     b_index_for_current_element = new_b.index(a[i])
#     if i != b_index_for_current_element:
#         new_b[b_index_for_current_element] = new_b[i]
#         new_b[i] = a[i]


# print(new_a)
# print(new_b)
    

    





