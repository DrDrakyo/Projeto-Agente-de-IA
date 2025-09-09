import customtkinter as ctk
from tkinter import filedialog
import requests
import pypdf

API_KEY = ""
API_URL = ""

# --- Configurações do tema ---
ctk.set_appearance_mode("dark")        
ctk.set_default_color_theme("blue")   

# Função para ler o PDF
def ler_pdf(caminho):
    with open(caminho, "rb") as f:
        reader = pypdf.PdfReader(f)
        texto = ""
        for pagina in reader.pages:
            texto += pagina.extract_text()
        return texto

# Selecionar e carregar o PDF
def selecionar_pdf():
    caminho = filedialog.askopenfilename(filetypes=[("Arquivos PDF", "*.pdf")])
    if caminho:
        texto = ler_pdf(caminho)
        texto_pdf.set(texto)
        adicionar_mensagem("📄 Documento carregado com sucesso!", "sistema")

# aba das mensagens no PDF
def adicionar_mensagem(texto, remetente):
    cor_bg = "#3a3a3a" if remetente == "usuario" else "#1f6aa5" if remetente == "gemini" else "#5c5c5c"

    bolha = ctk.CTkFrame(chat_frame, fg_color=cor_bg, corner_radius=12)
    mensagem = ctk.CTkLabel(bolha, text=texto, wraplength=500, justify="left", anchor="w")
    mensagem.pack(padx=10, pady=8)

    if remetente == "usuario":
        bolha.pack(anchor="w", pady=5, padx=10, fill="x")
    elif remetente == "gemini":
        bolha.pack(anchor="e", pady=5, padx=10, fill="x")
    else:  # sistema
        bolha.pack(anchor="c", pady=5)

    canvas.update_idletasks()
    canvas.yview_moveto(1)

# Enviar pergunta para a IA
def enviar_pergunta():
    doc = texto_pdf.get()
    pergunta = entrada.get().strip()
    if not pergunta:
        return
    entrada.delete(0, "end")
    adicionar_mensagem(pergunta, "usuario")

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"Documento:\n{doc}\n\nPergunta: {pergunta}"}
                ]
            }
        ]
    }

    resposta = requests.post(API_URL, json=payload)
    if resposta.status_code == 200:
        resposta_json = resposta.json()
        resposta_texto = resposta_json["candidates"][0]["content"]["parts"][0]["text"]
        adicionar_mensagem(resposta_texto, "gemini")
    else:
        adicionar_mensagem(f"Erro: {resposta.status_code}", "sistema")

#  Interface gráfica 
janela = ctk.CTk()
janela.title("PDF Chat")
janela.geometry("700x600")

texto_pdf = ctk.StringVar()

# topo – Botão para escolher PDF
top_bar = ctk.CTkFrame(janela)
top_bar.pack(fill="x", padx=10, pady=(10, 0))

btn_pdf = ctk.CTkButton(top_bar, text="📄 Carregar PDF", command=selecionar_pdf)
btn_pdf.pack(side="left")

# meio – Área de chat scrollável
chat_area = ctk.CTkFrame(janela, fg_color="transparent")
chat_area.pack(fill="both", expand=True, padx=10, pady=10)

canvas = ctk.CTkCanvas(chat_area, bg="#2b2b2b", highlightthickness=0)
scrollbar = ctk.CTkScrollbar(chat_area, orientation="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollable_frame = ctk.CTkFrame(canvas, fg_color="transparent")
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

def ajustar_scroll(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

scrollable_frame.bind("<Configure>", ajustar_scroll)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

chat_frame = scrollable_frame  # onde as bolhas aparecem

# Rrodapé – Entrada de pergunta e botão Enviar
entrada_frame = ctk.CTkFrame(janela)
entrada_frame.pack(fill="x", padx=10, pady=(0, 10))

entrada = ctk.CTkEntry(entrada_frame, placeholder_text="Digite sua pergunta...")
entrada.pack(side="left", fill="x", expand=True, padx=(0, 10))

btn_enviar = ctk.CTkButton(entrada_frame, text="Enviar", command=enviar_pergunta)
btn_enviar.pack(side="left")

janela.mainloop()
