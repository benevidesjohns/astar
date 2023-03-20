from node import Node
from queue import PriorityQueue
import map as mp
import pygame
import sys

# Constantes
LINE_COLOR = (70, 70, 70)
BACKGROUND_COLOR = (255, 255, 255)


class Player(pygame.sprite.Sprite):
    
    def __init__(self, position):
        super().__init__()
        self.image = pygame.image.load('img/link_18x18.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = position


# Funcao Heuristica -> Distancia de Manhattan
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


# Atualiza os nodes que definem o caminho encontrado pelo algoritmo
def reconstruct_path(path, draw, player_group):
    for node in path:
        player = Player((node.x, node.y))
        player_group.empty()
        player_group.add(player)
        draw()


# Astar algorithm
def algorithm(draw, grid, start, end, player_group):
    came_from = {}
    g_count = 0

    # Cria uma fila de prioridade e adiciona o node inicial (lista fechada)
    closed_list = PriorityQueue()
    closed_list.put((0, g_count, start))

    open_list = {start}

    # Calcula o G Score para cada node
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0

    # Calcula o F Score para cada node
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    # Executa enquanto a fila de prioridade nao estiver vazia
    while not closed_list.empty():

        # Verifica se deve sair do jogo
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Pega o node com mais prioridade da lista fechada e o remove da lista aberta
        current = closed_list.get()[2]
        open_list.remove(current)

        # Verifica se chegou no objetivo e constroi o caminho ate o mesmo
        if current == end:

            # Convert came_from dict in a list
            came_from_list = [current]
            while current in came_from:
                current = came_from[current]
                came_from_list.append(current)

            # Reconstruct path between start and end points
            reconstruct_path(reversed(came_from_list), draw, player_group)
            break

        # Calcula o F, G e H dos vizinhos do node atual
        for neighbor in current.neighbors:
            temp_g = g_score[current] + neighbor.terrain.cost

            if temp_g < g_score[neighbor]:
                came_from[neighbor] = current

                # Define o F e G Scores para cada vizinho
                g_score[neighbor] = temp_g
                f_score[neighbor] = temp_g + h(neighbor.get_pos(), end.get_pos())

                # Veifica se o vizinho nao esta na lista aberta
                if neighbor not in open_list:
                    g_count += temp_g
                    closed_list.put((f_score[neighbor], g_count, neighbor))
                    open_list.add(neighbor)


# Constroi o grid (matriz) com os nodes definidos no mapa
def make_grid(map, node_size):
    grid = []
    for i, row in enumerate(map.terrains):
        grid.append([])
        for j, terrain in enumerate(row):
            node = Node(i, j, node_size, terrain, map.size)
            grid[i].append(node)

    return grid


# Desenha a grade
def draw_grid(window, rows, width, node_size):
    for i in range(rows):
        pygame.draw.line(
            window, LINE_COLOR,  (0, i * node_size), (width, i * node_size)
        )
        for j in range(rows):
            pygame.draw.line(
                window, LINE_COLOR, (j * node_size, 0), (j * node_size, width)
            )


# Desenha na tela
def draw(window, width, map, node_size, player_group):
    window.fill(BACKGROUND_COLOR)

    # Desenha os nodes na tela
    for row in map.nodes:
        for node in row:
            node.draw(window)

    # Desenha a grade que separa os nodes
    draw_grid(window, map.size, width, node_size)

    # Desenha as imagens no mapa de Hyrule
    if not map.is_dungeon():
        for local, coord in map.points.items():
            (x, y) = coord
            node = map.nodes[x][y]
            if 'dungeon' in local:
                node.draw_image(window, 'entrada_dungeon')
            else:
                node.draw_image(window, local)

    # Desenha as imagens no mapa da Dungeon
    else:
        start = map.start_node
        end = map.end_node

        start.draw_image(window, 'entrada_dungeon')
        end.draw_image(window, f'pingente_{map.name}')

    # Desenha o personagem
    player_group.draw(window)

    # Atualiza a tela
    pygame.display.update()
    pygame.time.delay(100)


# Captura a posicao que o usuario clicou no grid
def get_clicked_pos(pos, rows, size):
    gap = size // rows
    y, x = pos

    row = x // gap
    col = y // gap

    return row, col


# Cria o jogador no ponto onde ele vai comecar
def make_start(x, y):
    player = Player((x, y))
    player_group = pygame.sprite.Group()
    player_group.add(player)
    return player_group


# Funcao principal
if __name__ == '__main__':

    # Define o mapa
    map = mp.hyrule()
    # map = mp.dungeon1()
    # map = mp.dungeon2()
    # map = mp.dungeon3()

    # Verifica o tamanho da janela do pygame (Hyrule -> 756, Dungeons -> 504)
    width = 504 if map.is_dungeon() else 756

    # Define a janela do pygame
    window = pygame.display.set_mode((width, width))
    pygame.display.set_caption("Zelda A*")

    # Define o grid (matriz de nodes)
    node_size = 18
    grid = make_grid(map, node_size)
    map.set_nodes(grid)

    # Define os nodes inicial e final
    map.set_start_end_nodes()
    start = map.start_node
    end = map.end_node

    # Define o jogador
    player_group = make_start(start.x, start.y)

    # Inicia o jogo
    while True:

        # Desenha o grid na tela
        draw(window, width, map, node_size, player_group)

        # Gerencia os eventos do pygame
        for event in pygame.event.get():

            # Encerra o jogo
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Seleciona o ponto de partida caso nao esteja setado
            if pygame.mouse.get_pressed()[0]:  # botao esquedo do mouse
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, map.size, width)
                node = map.nodes[row][col]

                if not start:
                    start = node
                    player_group = make_start(node.x, node.y)

            # Verifica as teclas do teclado
            if event.type == pygame.KEYDOWN:

                # SPACE - Inicia o jogo
                if event.key == pygame.K_SPACE and start and end:
                    for row in map.nodes:
                        for node in row:
                            node.update_neighbors(map.nodes)

                    # Executa o algoritmo da astar
                    algorithm(
                        lambda: draw(window, width, map, node_size, player_group),
                        map.nodes,
                        start,
                        end,
                        player_group
                    )

                # R - Reinicia o jogo
                if event.key == pygame.K_r:
                    player_group.empty()
                    start = None

                # ESC - Encerra o jogo
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
