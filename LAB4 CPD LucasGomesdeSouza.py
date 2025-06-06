import csv
import time
from typing import List

DATA_DIR = "players.csv"
SEARCH_DIR = "consultas.csv"


class Player:
    def __init__(self, id: int, name: str, position: List[str]):
        self.id = id
        self.name = name
        self.position = position


def polynomial_hash(number: int, mod: int, base: int = 31) -> int:
    hash_value = 0
    base_power = 1

    while number > 0:
        digit = number % 10
        hash_value = (hash_value + digit * base_power) % mod
        base_power = (base_power * base) % mod
        number //= 10

    return hash_value


def read_player(line: str) -> Player:
    fields = line.split(',')
    id = int(fields[0])
    name = fields[1]
    position = fields[2].split(',')
    return Player(id, name, position)


def read_players_from_csv(filename: str) -> List[Player]:
    players = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for line in reader:
            players.append(read_player(','.join(line)))
    return players


def read_search_from_csv(filename: str) -> List[int]:
    searches = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for line in reader:
            searches.append(int(line[0]))
    return searches


def record_statistics(times, occupancies, max_lists, avg_lists, filename):
    with open(filename, 'w') as file:
        file.write(f"{','.join([f'{t:.3f}' for t in times])}\n")
        file.write(f"{','.join([f'{o:.3f}' for o in occupancies])}\n")
        file.write(f"{','.join([str(m) for m in max_lists])}\n")
        file.write(f"{','.join([f'{a:.3f}' for a in avg_lists])}\n")


def build_and_search_hash_tables(M, players, searches):
    build_times = []
    occupancies = []
    max_lists = []
    avg_lists = []
    all_search_times = []
    search_comparisons = [[0] * len(M) for _ in range(len(searches))]
    search_names = ["NAO ENCONTRADO"] * len(searches)

    with open("estatisticas_consultas.txt", 'w') as search_stats:
        # Inicializar a lista de chaves não encontradas
        not_found_entries = []

        # Processamento da construção da tabela hash e busca
        for mod_idx, mod in enumerate(M):
            hash_table = [[] for _ in range(mod)]
            non_empty = 0
            max_list_size = 0
            total_entries = 0

            # Build hash table
            start_build = time.time()
            for player in players:
                hash_index = polynomial_hash(player.id, mod)
                hash_table[hash_index].append(player)
            end_build = time.time()
            build_time = (end_build - start_build) * 1000  # in milliseconds

            for hash_list in hash_table:
                if hash_list:
                    non_empty += 1
                    max_list_size = max(max_list_size, len(hash_list))
                    total_entries += len(hash_list)

            build_times.append(build_time)
            occupancies.append(non_empty / mod)
            max_lists.append(max_list_size)
            avg_lists.append(total_entries / non_empty if non_empty else 0)

            # Search in hash table
            start_search = time.time()
            for search_idx, id in enumerate(searches):
                hash_index = polynomial_hash(id, mod)
                comparisons = 0
                name = "NAO ENCONTRADO"

                if hash_table[hash_index]:
                    for player in hash_table[hash_index]:
                        comparisons += 1
                        if player.id == id:
                            name = player.name
                            break
                else:
                    comparisons += 1

                search_comparisons[search_idx][mod_idx] = comparisons
                if mod_idx == 0:
                    search_names[search_idx] = name

                # Se o jogador não foi encontrado, adiciona 99999 ao invés do ID
                if name == "NAO ENCONTRADO":
                    # Criar a linha no formato correto para cada tabela
                    not_found_entries.append((search_idx, comparisons))

            end_search = time.time()
            search_time = (end_search - start_search) * 1000  # in milliseconds
            all_search_times.append(search_time)

        # Escrever os tempos de busca para cada tabela
        search_stats.write(','.join([f'{st:.3f}' for st in all_search_times]) + "\n")

        # Escrever as informações detalhadas das consultas
        for search_idx, id in enumerate(searches):
            search_stats.write(f"{id},{search_names[search_idx]}")
            for mod_idx in range(len(M)):
                search_stats.write(f",{search_comparisons[search_idx][mod_idx]}")
            search_stats.write("\n")

        # Escrever as chaves não encontradas no mesmo arquivo, agora para cada M
        for search_idx, _ in enumerate(searches):
            if search_names[search_idx] == "NAO ENCONTRADO":
                search_stats.write(f"99999,NAO ENCONTRADO,{','.join(str(search_comparisons[search_idx][mod_idx]) for mod_idx in range(len(M)))}\n")

    # Gravar as estatísticas de construção
    record_statistics(build_times, occupancies, max_lists, avg_lists, "estatisticas_construcao.txt")


def main():
    M = [3793, 6637, 9473, 12323, 15149]
    players = read_players_from_csv(DATA_DIR)
    searches = read_search_from_csv(SEARCH_DIR)

    build_and_search_hash_tables(M, players, searches)


if __name__ == "__main__":
    main()
