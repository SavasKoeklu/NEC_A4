import random
import tsplib95

class GeneticAlgorithm:

     # Todo: chnage name of activation function to "fact"
    def __init__(self, problem, initial_population_size=100):
        # the size of the initial population
        self.initial_population_size = initial_population_size
        self.problem = problem

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
            population.append(new_list)
        return population
        

    def fitness_for_route(distance):
        # requirements fitness function to maximize when the distance of the route minimizes
        fitness = 1/distance
        return fitness
    


problem = tsplib95.load('datasets/gr17.tsp.txt')
Alg = GeneticAlgorithm(problem,20)

print(Alg.create_initial_population())


