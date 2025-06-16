import pygame
import socket
import pickle
import sys

class GameClient:
    def __init__(self, host='10.0.0.10', port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        data = self.client.recv(1024)
        resposta = pickle.loads(data)
        self.id = resposta['id']
        self.x = 300
        self.estado = {}

    def enviar_movimento(self):
        comando = {'tipo': 'mover', 'x': self.x}
        self.client.sendall(pickle.dumps(comando))

    def receber_estado(self):
        data = self.client.recv(4096)
        self.estado = pickle.loads(data)

    def executar(self):
        pygame.init()
        tela = pygame.display.set_mode((600, 600))
        pygame.display.set_caption(f"Player {self.id}")
        fonte = pygame.font.SysFont(None, 36)
        clock = pygame.time.Clock()

        rodando = True
        while rodando:
            tela.fill((0, 0, 0))
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False

            self.receber_estado()

            if not self.estado.get('jogo_iniciado', False):
                contagem = self.estado.get('contagem_regressiva', -1)
                if contagem == -1:
                    mensagem = "Aguardando outro jogador..."
                elif contagem >= 0:
                    if contagem == 0:
                        mensagem = "GO!"
                    else:
                        mensagem = str(contagem)
                else:
                    mensagem = "Preparando jogo..."

                texto = fonte.render(mensagem, True, (255, 255, 0))
                tela.blit(texto, (250, 250))
                pygame.display.flip()
                clock.tick(1 if contagem >= 0 else 30)
                continue

            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_a]:
                self.x -= 5
            if teclas[pygame.K_d]:
                self.x += 5

            self.enviar_movimento()

            for pid, jogador in self.estado['players'].items():
                cor = (0, 255, 0) if int(pid) == self.id else (0, 0, 255)
                pygame.draw.rect(tela, cor, (jogador['x'], 550, 40, 20))

            for ast in self.estado['asteroids']:
                pygame.draw.rect(tela, (255, 0, 0), (ast['x'], ast['y'], 20, 20))

            if self.estado.get('vencedor') is not None:
                if int(self.estado['vencedor']) == self.id:
                    msg = "Você venceu!"
                else:
                    msg = "Você perdeu!"
                texto = fonte.render(msg, True, (255, 255, 255))
                tela.blit(texto, (220, 300))

            pygame.display.flip()
            clock.tick(30)

if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    GameClient().executar()
