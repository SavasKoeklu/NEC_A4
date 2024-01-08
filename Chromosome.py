class Chromosome:

    def __init__(self, route, problem):
        self.route = route
        self.problem = problem
        self.fitness = self.fitness_for_route(route)

    def fitness_for_route(self, route):
        # requirements fitness function to maximize when the distance of the route minimizes
        fitness = 1 / float(self.problem.trace_tours([route])[0])
        return fitness

    def get_distance(self):
        return self.problem.trace_tours([self.route])[0]

    def set_route(self, route):
        self.route = route
        self.fitness = self.fitness_for_route(route)

    def get_as_tuple(self):
        return self.route, self.fitness

    def route_swap_positions(self, position1, position2):
        self.route[position1], self.route[position2] = self.route[position2], self.route[position1]
        self.fitness = self.fitness_for_route(self.route)
