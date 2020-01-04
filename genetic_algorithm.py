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
            second_city += 1

    # funkcja zlicza koszt
    def count_cost(self, mapping, m):

        for key, demand_parts_for_city in self.cities_demand.items():
            for path_number in range(0, 7):
                for edges_number in mapping[key][path_number]:
                    self.demand_edges_list[edges_number] += self.cities_demand[key][path_number]

        self.demand_edges_list = [math.floor(demand_edge / m) for demand_edge in self.demand_edges_list]
        self.cost = sum(self.demand_edges_list)

    # parametr disintegrate określa - Dezagregacja zapotrzebowań pary miast na ścieżki = True
    #                               - Agregacja zapotrzebowań pary miast na ścieżkę = False
    def get_demand_fractions_list(self, city_demand, disintegrate):
        if disintegrate:
            random_list_of_demand_fractions = np.random.random(7)
            random_list_of_demand_fractions /= random_list_of_demand_fractions.sum()
            demand_fractions_list = random_list_of_demand_fractions * city_demand
        else:
            path_number = random.randint(0, 6)
            demand_fractions_list = np.zeros(7)
            demand_fractions_list[path_number] = city_demand

        return np.ndarray.tolist(demand_fractions_list)


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


if __name__ == '__main__':
    # demand.txt - plik z zapotrzebowaniem na pary miast
    all_demand = np.genfromtxt('demand.txt', delimiter='\n')
    mapping = Mapping()
    chromosome = Chromosome()
    chromosome.fill_chromosome(all_demand)
    chromosome.count_cost(mapping.demand_mapping, 10000)
