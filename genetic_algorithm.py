from collections import defaultdict
from itertools import repeat
import numpy as np
import random
import math


class Chromosome:
    def __init__(self):
        # słownik z listami zpotrzebowań(rozłożonymi na ścieżki) na każdą parę miast
        self.cities_demand = {}
        # lista ze stanem końcowym na krawędziach- 0 - nie przekroczyło przepustowości, 1, 2, 3... - znaczy tyle dodatkowo kabli trzeba położyć na krawędzi (mamy 18 krawędzi)
        self.demand_edges_list = list(repeat(0, 18))
        # cost - suma z demand_edges_list, czyli ilość kabli do położenia
        self.cost = 0
        # słownik: para miast - całość zapotrzebowania dla pary
        self.full_demand_by_pair = {}

    # funkacja wypełnia chromosom
    def fill_chromosome(self, demand_list, disintegrate=True):
        first_city = 0
        second_city = 1
        for demand in demand_list:
            if second_city > 11:
                first_city += 1
                second_city = first_city + 1
            self.cities_demand[f'demand_{first_city}_{second_city}'] = (
                self.get_demand_fractions_list(demand, disintegrate))
            # zamapiętaj w słowniku zapotrzebowanie dla pary miast
            self.full_demand_by_pair[f'demand_{first_city}_{second_city}'] = demand
            second_city += 1

        # print(self.cities_demand)
        # print(self.full_demand_by_pair)

    # funkcja zlicza koszt
    def count_cost(self, mapping, m):

        for key, demand_parts_for_city in self.cities_demand.items():
            for path_number in range(0, 7):
                for edges_number in mapping[key][path_number]:
                    # obciążenie dodane do krawędzi =
                    # ułamek zapotrzebowania dla pary jaka przez nią idzie * całkowite obciążenie

                    print(self.cities_demand[key][path_number])
                    print(self.full_demand_by_pair[key])
                    print(self.cities_demand[key][path_number] * self.full_demand_by_pair[key])

                    self.demand_edges_list[edges_number] += (
                                self.cities_demand[key][path_number] * self.full_demand_by_pair[key])

        self.demand_edges_list = [math.ceil(demand_edge / m) for demand_edge in self.demand_edges_list]
        self.cost = sum(self.demand_edges_list)

        return self.cost

    def crossover(self, parent_a, parent_b, crossover_probability):

        # gen to rozkład zapotrzebowania na ścieżki dla pary miast - element słownika cities_demand
        for gene_key, gene_val in parent_a.cities_demand.items():
            if np.random.random_sample() < crossover_probability:
                self.cities_demand[gene_key] = gene_val
            else:
                self.cities_demand[gene_key] = parent_b.cities_demand[gene_key]

        # liczone przy ocenianiu
        self.demand_edges_list = list(repeat(0, 18))

        # sumaryczne zapotrzebowanie dla pary się nie zmienia
        self.full_demand_by_pair = parent_a.full_demand_by_pair

    def mutation(self, mutation_probability, disintegrate=True):
        for gene_key, gene_val in self.cities_demand.items():
            if np.random.random_sample() < mutation_probability:
                self.cities_demand[gene_key] = (
                    self.get_demand_fractions_list(self.full_demand_by_pair[gene_key], disintegrate))

    # parametr disintegrate określa - Dezagregacja zapotrzebowań pary miast na ścieżki = True
    #                               - Agregacja zapotrzebowań pary miast na ścieżkę = False
    def get_demand_fractions_list(self, city_demand, disintegrate):

        # część zapotrzebowania jako ułamek

        if disintegrate:
            points_of_division = np.random.random(6)
            points_of_division.sort()
            demand_fractions_list = [points_of_division[0]]
            for i in range(1, 6):
                demand_fractions_list.append(points_of_division[i] - points_of_division[i - 1])
            demand_fractions_list.append(1 - points_of_division[5])

            return demand_fractions_list

        else:
            path_number = random.randint(0, 6)
            demand_fractions_list = np.zeros(7)
            demand_fractions_list[path_number] = 1
            np.ndarray.tolist(demand_fractions_list)

        return demand_fractions_list


class Mapping:
    def __init__(self):
        self.links_dict = {
            'Link_0_10': 0,
            'Link_0_2': 1,
            'Link_1_2': 2,
            'Link_1_7': 3,
            'Link_1_10': 4,
            'Link_2_9': 5,
            'Link_3_4': 6,
            'Link_3_6': 7,
            'Link_3_11': 8,
            'Link_4_8': 9,
            'Link_4_10': 10,
            'Link_5_8': 11,
            'Link_5_10': 12,
            'Link_6_10': 13,
            'Link_6_11': 14,
            'Link_7_9': 15,
            'Link_7_11': 16,
            'Link_0_5': 17
        }
        # słownik z mapowaniem - dla każdego demand lista list z indeksami krawędzi odpowiednio dla kazðego P_0, P_1 itd
        self.demand_mapping = defaultdict(list)
        self.fill_demand_mapping()

    def fill_demand_mapping(self):
        first_city = 0
        second_city = 1
        iterator = 0
        with open('mapping_links.txt', 'r') as reader_file:
            for line in reader_file:
                row = line.strip().split(' ')
                if iterator > 6:
                    if second_city == 11:
                        first_city += 1
                        second_city = first_city + 1
                    else:
                        second_city += 1
                    iterator = 0

                list_of_links = [self.links_dict.get(link) for link in row[2:len(row) - 1]]
                self.demand_mapping[f'demand_{first_city}_{second_city}'].append(list_of_links)
                iterator += 1
        # print(self.demand_mapping)


class Algorithm:
    def __init__(self, modularity, population_number, crossover_probability, mutation_probabilty):
        self.modularity = modularity
        self.population_number = population_number
        self.crossover_probability = crossover_probability
        self.mutation_probabilty = mutation_probabilty

        # demand.txt - plik z zapotrzebowaniem na pary miast
        self.all_demand = np.genfromtxt('demand.txt', delimiter='\n')
        self.mapping = Mapping().demand_mapping

        # populacja początkowa
        self.population = []

        for _ in range(self.population_number):
            self.population.append(Chromosome())

        for chromosome in self.population:
            chromosome.fill_chromosome(self.all_demand)

    def run(self, iterations):

        # przykład  - porównanie dwóch rodziców i ich dziecka

        # print(self.population[0].cities_demand)
        # print(self.population[1].cities_demand)
        # child = Chromosome()
        # child.crossover(self.population[0], self.population[1], self.crossover_probability)
        # child.mutation(self.mutation_probabilty)
        # print(child.cities_demand)

        for i in range(iterations):

            # tyle dzieci z krzyżowań ile osobników w populacji - populacja się podwaja

            children = []
            for _ in self.population:
                parent_a = self.population[np.random.randint(self.population_number)]
                parent_b = self.population[np.random.randint(self.population_number)]
                child = Chromosome()
                child.crossover(parent_a, parent_b, self.crossover_probability)
                children.append(child)

            self.population = self.population + children

            # mutacja
            for p in self.population:
                p.mutation(self.mutation_probabilty)

            # sortowanie od najlepiej do najgorzej przystosowanych
            self.population.sort(key=lambda p: p.count_cost(self.mapping, self.modularity), reverse=True)

            # przycięcie populacji do pierwotnego rozmiaru
            self.population = self.population[:self.population_number]

        for p in self.population:
            print(p.cities_demand)
            print(p.cost)


if __name__ == '__main__':
    #parametry: m, populacja początkowa, prawdopodobieństwo krzyżowania i mutacji
    algorithm = Algorithm(10, 10, 0.4, 0.2)
    algorithm.run(10)
