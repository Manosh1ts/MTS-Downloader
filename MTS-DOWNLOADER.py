import os
import tkinter as tk
from tkinter import messagebox, ttk
from threading import Thread, Event
import webbrowser
import subprocess
import queue

# Variáveis globais para o progresso da playlist
total_musicas = 0
musicas_baixadas = 0
cancelar_evento = Event()
fila_msg = queue.Queue()

# Função para baixar música ou playlist
def baixar_musica():
    global total_musicas, musicas_baixadas, cancelar_evento
    cancelar_evento.clear()  # Reseta o evento de cancelamento

    # Obtém o link inserido pelo usuário
    url = entrada_url.get()
    if not url.strip():
        messagebox.showwarning("Aviso", "Por favor, insira um link válido!")
        return

    # Reseta os contadores de progresso
    total_musicas = 0
    musicas_baixadas = 0
    progresso_label.config(text="Fila: 0/0")  # Reseta a exibição da fila

    # Define a barra como indeterminada
    progresso.config(mode='indeterminate')
    progresso.start(10)  # Velocidade do movimento
    botao_baixar.config(state=tk.DISABLED)  # Desabilita o botão enquanto o download ocorre
    botao_cancelar.config(state=tk.NORMAL)  # Habilita o botão de cancelar

    # Função para realizar o download em uma thread separada
    def realizar_download():
        global total_musicas, musicas_baixadas
        pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")

        # Hook para acompanhar o progresso
        def progress_hook(d):
            global musicas_baixadas
            if cancelar_evento.is_set():
                raise subprocess.CalledProcessError("Download cancelado pelo usuário.")
            if d['status'] == 'finished':
                musicas_baixadas += 1
                fila_msg.put(f"Fila: {musicas_baixadas}/{total_musicas}")

        # Construção do comando yt-dlp
        yt_dlp_command = [
            "yt-dlp",
            "-x",  # Extrair áudio
            "--audio-format", "mp3",  # Formato de áudio mp3
            "--audio-quality", "0",  # Qualidade máxima
            "--output", os.path.join(pasta_downloads, "%(title)s.%(ext)s"),  # Caminho de saída
            url
        ]

        try:
            # Realiza o download
            process = subprocess.Popen(yt_dlp_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for line in process.stdout:
                progress_hook({'status': 'finished'})  # Simula o progresso para o exemplo

            process.wait()
            fila_msg.put("concluido")
        except subprocess.CalledProcessError:
            fila_msg.put("cancelado")
        except Exception as e:
            fila_msg.put(f"Erro: {e}")

    # Cria uma thread para o download
    thread = Thread(target=realizar_download)
    thread.daemon = True
    thread.start()

# Função para cancelar o download
def cancelar_download():
    cancelar_evento.set()

# Função para processar mensagens da fila
def atualizar_interface():
    try:
        msg = fila_msg.get_nowait()
        if msg == "concluido":
            messagebox.showinfo("Sucesso", "Download concluído!")
            progresso.stop()
            progresso.config(mode='determinate')
            botao_baixar.config(state=tk.NORMAL)
            botao_cancelar.config(state=tk.DISABLED)
        elif msg == "cancelado":
            messagebox.showinfo("Cancelado", "O download foi cancelado.")
            progresso.stop()
            progresso.config(mode='determinate')
            botao_baixar.config(state=tk.NORMAL)
            botao_cancelar.config(state=tk.DISABLED)
        elif "Erro" in msg:
            messagebox.showerror("Erro", msg)
            progresso.stop()
            progresso.config(mode='determinate')
            botao_baixar.config(state=tk.NORMAL)
            botao_cancelar.config(state=tk.DISABLED)
        else:
            progresso_label.config(text=msg)
    except queue.Empty:
        pass
    janela.after(100, atualizar_interface)

# Função para abrir os créditos no navegador
def abrir_creditos():
    webbrowser.open("https://bit.ly/Manoshits")  # Substitua pelo seu canal do YouTube

# Configuração da janela principal
janela = tk.Tk()
janela.title("Downloader de Músicas By ManoshitsDev")
janela.geometry("600x400")
janela.config(bg='#2A2A2A')  # Fundo cinza escuro

# Define o ícone da janela
icone_path = os.path.join(os.getcwd(), "icone.ico")
janela.iconbitmap(icone_path)

# Função para mudar a cor do botão ao passar o mouse
def on_enter(button):
    button.config(bg='#8A2BE2')  # Cor roxa ao passar o mouse

def on_leave(button):
    button.config(bg='#4B0082')  # Cor roxa escura ao tirar o mouse

# Componentes da GUI
tk.Label(janela, text="Insira o link da música ou playlist: S2", font=("Arial", 14), fg="white", bg="#2A2A2A").pack(pady=20)

entrada_url = tk.Entry(janela, width=50, font=("Arial", 12), bd=2, relief="solid")
entrada_url.pack(pady=5)

botao_baixar = tk.Button(janela, text="Baixar +", command=baixar_musica, font=("Arial", 12), bg='#4B0082', fg='white', bd=2, relief="solid")
botao_baixar.pack(pady=20)
botao_baixar.bind("<Enter>", lambda e: on_enter(botao_baixar))
botao_baixar.bind("<Leave>", lambda e: on_leave(botao_baixar))

# Botão de Cancelar
botao_cancelar = tk.Button(janela, text="Cancelar X", command=cancelar_download, font=("Arial", 12), bg='#4B0082', fg='white', bd=2, relief="solid", state=tk.DISABLED)
botao_cancelar.pack(pady=10)
botao_cancelar.bind("<Enter>", lambda e: on_enter(botao_cancelar))
botao_cancelar.bind("<Leave>", lambda e: on_leave(botao_cancelar))

# Barra de Progresso Indeterminada
style = ttk.Style()
style.theme_use('default')
style.configure("TProgressbar", thickness=10, background='#8A2BE2', troughcolor='#2A2A2A', bordercolor='#2A2A2A')

progresso = ttk.Progressbar(janela, length=400, mode='determinate', style="TProgressbar")
progresso.pack(pady=20)

# Label para exibir o progresso da fila
progresso_label = tk.Label(janela, text="Fila: 0/0", font=("Arial", 12), fg="white", bg="#2A2A2A")
progresso_label.pack(pady=10)

# Botão de Créditos
botao_creditos = tk.Button(janela, text="Créditos", command=abrir_creditos, font=("Arial", 12), bg='#8A2BE2', fg='white', bd=2, relief="solid")
botao_creditos.pack(pady=10)
botao_creditos.bind("<Enter>", lambda e: on_enter(botao_creditos))
botao_creditos.bind("<Leave>", lambda e: on_leave(botao_creditos))

# Inicia o processamento da fila
janela.after(100, atualizar_interface)

# Executa a interface gráfica
janela.mainloop()
