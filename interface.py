import tkinter as tk
from tkinter import messagebox
from extrator import Extractor
import os
from dotenv import load_dotenv

def extract_text_action():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Erro", "Por favor, insira uma URL.")
        return

    try:
        text = extractor.extract_text(url, doc_type="txt", save_path="./output")
        messagebox.showinfo("Sucesso", "Texto extraído e salvo em ./output/extracted_text.txt")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao extrair texto: {e}")

def extract_images_action():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Erro", "Por favor, insira uma URL.")
        return

    try:
        image_urls = extractor.extract_images(url, save_path="./output/images", include_descriptions=False)
        messagebox.showinfo("Sucesso", f"Imagens extraídas e salvas em ./output/images. Total: {len(image_urls)}")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao extrair imagens: {e}")

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("A chave de API não foi encontrada no arquivo .env.")

# Inicializa o extrator
extractor = Extractor(api_key=api_key)

# Configuração da interface gráfica
root = tk.Tk()
root.title("WebDataDrill")

# Título
title_label = tk.Label(root, text="WebDataDrill", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

# Entrada de URL
url_label = tk.Label(root, text="Insira a URL:")
url_label.pack()
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Botões de ação
text_button = tk.Button(root, text="Extrair Texto", command=extract_text_action)
text_button.pack(pady=5)

images_button = tk.Button(root, text="Extrair Imagens", command=extract_images_action)
images_button.pack(pady=5)

# Inicia o loop da interface gráfica
root.mainloop()
