from collections import defaultdict
from itertools import repeat
import numpy as np
import random
import math
import sys


class Chromosome:
    """
    Klasa definiująca pojedynczy chromosom.
    :param cities_demand: słownik z listami zapotrzebowań (rozłożonymi na ścieżki) na każdą parę miast
    :param demand_edges_list: lista liczb kabli - liczba kabli, którą trzeba położyć na danej krawędzi, znajduje się na miejscu w liście odpowiadającym numerowi krawędzi
    :param cost: sumaryczna liczba kabli
    :param full_demand_by_pair: sumaryczne zapotrzebowanie dla pary miast
    :type cities_demand: dict
    :type demand_edges_list: list
    :type cost: int
    :type full_demand_by_pair: dict
    """
    def __init__(self):
        """
        Inicjuje pola klasy.
        """

        self.cities_demand = {}
        self.demand_edges_list = list(repeat(0, 18))
        self.cost = 0
        self.full_demand_by_pair = {}

    # funkacja wypełnia chromosom
    def fill_chromosome(self, demand_list, disintegrate=True):
        """
        Wypełnia rozkład zapotrzebowań na ścieżki (cities_demand) i przypisanie sumarycznego zapotrzebowania dla pary miast (full_demand_by_pair).
        :param demand_list: lista sumarycznych zapotrzebowań w kolejności odpowiadającej przyjętej kolejności par miast
        :param disintegrate: czy zapotrzebowanie dla każdej pary ma być rozłożone między ścieżkami, czy ma być wybrana jedna
        :type demand_list: list
        :type disintegrate: boolean
        """
        first_city = 0
        second_city = 1
        for demand in demand_list:
            if second_city > 11:
                first_city += 1
                second_city = first_city + 1
            self.cities_demand[f'demand_{first_city}_{second_city}'] = (
                self.get_demand_fractions_list(demand, disintegrate))
            self.full_demand_by_pair[f'demand_{first_city}_{second_city}'] = demand
            second_city += 1

    def count_cost(self, mapping, m):
        """
        Zlicza koszt realizacji sieci według danych w chromosomie (liczbę kabli).
        :param mapping: mapowanie krawędzi na ścieżki między miastami
        :param m: modularność krawędzi
        :type mapping: list
        :type m: int
        :return: sumaryczny koszt
        :rtype: int
        """

        for key, demand_parts_for_city in self.cities_demand.items():
            for path_number in range(0, 7):
                for edges_number in mapping[key][path_number]:
                    # obciążenie dodane do krawędzi =
                    # ułamek zapotrzebowania dla pary jaka przez nią idzie * całkowite obciążenie

                    self.demand_edges_list[edges_number] += (
                                self.cities_demand[key][path_number] * self.full_demand_by_pair[key])

        self.demand_edges_list = [math.ceil(demand_edge / m) for demand_edge in self.demand_edges_list]
        self.cost = sum(self.demand_edges_list)

        return self.cost

    def crossover(self, parent_a, parent_b, crossover_probability):
        """
        Przeprowadza krzyżowanie wielopunktowe dwóch rodziców, których dzieckiem będzie dany chromosom. Wypełnia te same pola, co fill_chromosome.
        :param parent_a: rodzic
        :param parent_b: rodzic
        :type parent_a: Chromosome
        :type parent_b: Chromosome
        :param crossover_probability: prawdopodobieństwo krzyżowania
        :type crossover_probability: float
        """

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
        """
        Przeprowadza mutację. Zgodnie z prawdopodobieństwem mutacji dla każdego genu (rozkładu zapotrzebowań dla pary miast) zastępuje go nowym.
        :param mutation_probability: prawdopodobieństwo zastąpienia genu
        :param disintegrate: czy zapotrzebowanie dla każdej pary jest rozłożone między ścieżkami, czy jest wybrana jedna
        :param mutation_probability: float
        :param disintegrate: boolean
        """
        for gene_key, gene_val in self.cities_demand.items():
            if np.random.random_sample() < mutation_probability:
                self.cities_demand[gene_key] = (
                    self.get_demand_fractions_list(self.full_demand_by_pair[gene_key], disintegrate))


    def get_demand_fractions_list(self, city_demand, disintegrate):
        """
        Zależnie od wartości parametru disintegrate:
        * True - rozlosowuje między ścieżkami dla zadanej pary miast, jaki ułamek zapotrzebowania mają spełniać
        * False - losuje, która ścieżka ma spełniać zapotrzebowanie
        :param city_demand: para miast, dla której ma być określony rozkład zapotrzebowania na ścieżki
        :param disintegrate: określa tryb działania
        :type city_demand:
        :type disintegrate:
        :return: rozkład zapotrzebowania na ścieżki
        :rtype: array
        """

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
    """
    Klasa zawierająca przyjęte numery ścieżek i mapowanie numerów krawędzi na ścieżki między parami miast.
    :param links_dict: mapowanie krawędzi na przyjęte numery krawędzi
    :type links_dict: dict
    :param demand_mapping: mapowanie numerów krawędzi na ścieżki między parami miast (słownik list)
    :type demand_mapping: dict
    """
    def __init__(self):
        """
        Przypisuje mapowania do zmiennych.
        """
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

        self.demand_mapping = defaultdict(list)
        self.fill_demand_mapping()

    def fill_demand_mapping(self):
        """
        Realizuje mapowanie numerów krawędzi na ścieżki między parami miast.
        """
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


class Algorithm:
    """
    Klasa algorytmu genetycznego.
    :param modularity: przepustowość jednego kabla
    :type modularity: int
    :param population_number: początkowa liczność populacji
    :type population_number: int
    :param crossover_probability: prawdopodobieństwo krzyżowania
    :type crossover_probability: float
    :param mutation_probabilty: prawdopodobieństwo zastąpienia genu
    :type mutation_probabilty: float
    :param all_demand: sumaryczne zapotrzebowania dla kolejnych par miast
    :param all_demand: list
    :param mapping: mapowanie krawędzi na ścieżki między parami miast
    :type mapping: dict
    :param population: populacja - tablica chromosomów
    :type population: array

    """
    def __init__(self, modularity, population_number, crossover_probability, mutation_probabilty):
        """
        Inicjuje pola klaasy.
        """
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
        """
        Wykonuje algorytm przez zadaną liczbę iteracji.
        :param iterations: liczba iteracji algorytmu
        :type iterations: int
        """

        # przykład  - porównanie dwóch rodziców i ich dziecka

        # print(self.population[0].cities_demand)
        # print(self.population[1].cities_demand)
        # child = Chromosome()
        # child.crossover(self.population[0], self.population[1], self.crossover_probability)
        # child.mutation(self.mutation_probabilty)
        # print(child.cities_demand)

        with open('results.txt', 'w') as file:
            file.write('licznosc_populacji\tprawd_krzyzowania\tprawd_mutacji\tmin_koszt\n')

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
            self.population.sort(key=lambda p: p.count_cost(self.mapping, self.modularity), reverse=False)

            # przycięcie populacji do pierwotnego rozmiaru
            self.population = self.population[:self.population_number]

            with open('results.txt', 'a') as file:
                file.write('{}\t{}\t{}\t{}\n'.format(len(self.population), self.crossover_probability, self.mutation_probabilty, self.population[0].cost))

        for p in self.population:
            print(p.cities_demand)
            print(p.cost)


if __name__ == '__main__':
    """
    Uruchamia algorytm z parametrami podanymi przy uruchomieniu programu lub z domyślnymi.
    Parametry uruchomienia:
    * modularność, 
    * populacja początkowa, 
    * prawdopodobieństwo krzyżowania, 
    * prawdopodobieństwo mutacji,
    * liczba iteracji.
    """
    if len(sys.argv) > 1:
        algorithm = Algorithm(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        algorithm.run(sys.argv[5])
    else:
        algorithm = Algorithm(100, 10, 0.4, 0.0)
        algorithm.run(500)
