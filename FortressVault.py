import customtkinter as ctk
import sqlite3
import random
import string
import csv
from tkinter import ttk, messagebox, filedialog

# ================= BANCO =================
conexao = sqlite3.connect("db.db") # <---- Caminho do banco de dados
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Geren (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Site TEXT,
    Login TEXT,
    Senha TEXT
)
""")
conexao.commit()

# ================= APP =================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.iconbitmap("icon.ico")
app.geometry("900x480")
app.title("FortressVault - Gerenciador de Senhas")

# ================= ABAS =================
tabs = ctk.CTkTabview(app)
tabs.pack(fill="both", expand=True, padx=10, pady=10)

aba_logins = tabs.add("Logins")
aba_gerador = tabs.add("Gerador de Senhas")
aba_csv = tabs.add("Importar / Exportar CSV")
aba_config = tabs.add("Configurações")

# =====================================================
# ================= ABA LOGINS ========================
# =====================================================

def visualizar_registro(event=None):
    selecionado = tabela.focus()
    if not selecionado:
        return

    id_, site, login, senha = tabela.item(selecionado)["values"]

    win = ctk.CTkToplevel(app)
    win.title("Detalhes do Registro")
    win.geometry("360x400")
    win.grab_set()

    def copiar(texto):
        win.clipboard_clear()
        win.clipboard_append(texto)
        win.update()
        messagebox.showinfo("Copiado", "Texto copiado para a área de transferência")

    # SITE
    ctk.CTkLabel(win, text="Site").pack(anchor="w", padx=20, pady=(15, 0))
    e_site = ctk.CTkEntry(win)
    e_site.insert(0, site)
    e_site.configure(state="readonly")
    e_site.pack(fill="x", padx=20)
    ctk.CTkButton(win, text="Copiar Site", command=lambda: copiar(site)).pack(pady=5)

    # LOGIN
    ctk.CTkLabel(win, text="Login").pack(anchor="w", padx=20, pady=(10, 0))
    e_login = ctk.CTkEntry(win)
    e_login.insert(0, login)
    e_login.configure(state="readonly")
    e_login.pack(fill="x", padx=20)
    ctk.CTkButton(win, text="Copiar Login", command=lambda: copiar(login)).pack(pady=5)

    # SENHA
    ctk.CTkLabel(win, text="Senha").pack(anchor="w", padx=20, pady=(10, 0))
    e_senha = ctk.CTkEntry(win, show="*")
    e_senha.insert(0, senha)
    e_senha.configure(state="readonly")
    e_senha.pack(fill="x", padx=20)

    def mostrar_senha():
        e_senha.configure(show="")

    def ocultar_senha():
        e_senha.configure(show="*")

    frame_senha = ctk.CTkFrame(win, fg_color="transparent")
    frame_senha.pack(pady=5)

    ctk.CTkButton(frame_senha, text="Mostrar", width=80, command=mostrar_senha).pack(side="left", padx=5)
    ctk.CTkButton(frame_senha, text="Ocultar", width=80, command=ocultar_senha).pack(side="left", padx=5)
    ctk.CTkButton(win, text="Copiar Senha", command=lambda: copiar(senha)).pack(pady=8)


# ----- Barra de Pesquisa -----
frame_pesquisa = ctk.CTkFrame(aba_logins)
frame_pesquisa.pack(fill="x", padx=10, pady=(10, 0))

pesquisa_var = ctk.StringVar()

entry_pesquisa = ctk.CTkEntry(
    frame_pesquisa,
    placeholder_text="Pesquisar site, login ou senha...",
    textvariable=pesquisa_var
)
entry_pesquisa.pack(fill="x", expand=True, padx=10, pady=8)

# ----- Layout principal -----
main_frame = ctk.CTkFrame(aba_logins)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

frame_tabela = ctk.CTkFrame(main_frame)
frame_tabela.pack(side="left", fill="both", expand=True)

frame_botao = ctk.CTkFrame(main_frame, width=180)
frame_botao.pack(side="right", fill="y", padx=10)

# ----- Scrollbars -----
scroll_y = ttk.Scrollbar(frame_tabela, orient="vertical")
scroll_y.pack(side="right", fill="y")

scroll_x = ttk.Scrollbar(frame_tabela, orient="horizontal")
scroll_x.pack(side="bottom", fill="x")

# ----- Tabela -----
colunas = ("Id", "Site", "Login", "Senha")

tabela = ttk.Treeview(
    frame_tabela,
    columns=colunas,
    show="headings",
    yscrollcommand=scroll_y.set,
    xscrollcommand=scroll_x.set
)
tabela.pack(fill="both", expand=True)

scroll_y.config(command=tabela.yview)
scroll_x.config(command=tabela.xview)

#----------Atualizar IDs----------
def refresh_ids():
    try:
        resposta = messagebox.askyesno(
            "Atenção",
            "Isso vai reorganizar TODOS os IDs.\n\nDeseja continuar?"
        )
        if not resposta:
            return

        conexao = sqlite3.connect("db.db")
        cursor = conexao.cursor()

        cursor.execute("BEGIN TRANSACTION;")

        # cria tabela temporária com a MESMA estrutura
        cursor.execute("""
        CREATE TABLE Geren_temp (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Site TEXT,
            Login TEXT,
            Senha TEXT
        );
        """)

        # copia os dados com IDs sequenciais
        cursor.execute("""
        INSERT INTO Geren_temp (Site, Login, Senha)
        SELECT Site, Login, Senha
        FROM Geren
        ORDER BY Id;
        """)

        cursor.execute("DROP TABLE Geren;")
        cursor.execute("ALTER TABLE Geren_temp RENAME TO Geren;")

        conexao.commit()
        conexao.close()

        carregar_dados()
        messagebox.showinfo("Sucesso", "IDs reorganizados com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao reorganizar IDs:\n{e}")


for col in colunas:
    tabela.heading(col, text=col)
    tabela.column(col, width=180 if col != "Id" else 50)

# ----- Funções -----
def carregar_dados(filtro=""):
    tabela.delete(*tabela.get_children())

    if filtro:
        cursor.execute("""
            SELECT * FROM Geren
            WHERE Site LIKE ?
               OR Login LIKE ?
               OR Senha LIKE ?
        """, (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%"))
    else:
        cursor.execute("SELECT * FROM Geren")

    for row in cursor.fetchall():
        tabela.insert("", "end", values=row)
# ----- Duplo clique para visualizar registro -----
tabela.bind("<Double-1>", visualizar_registro)

def atualizar_pesquisa(*args):
    carregar_dados(pesquisa_var.get())

pesquisa_var.trace_add("write", atualizar_pesquisa)
carregar_dados()

# ----- CRUD -----
def abrir_formulario():
    form = ctk.CTkToplevel(app)
    form.title("Adicionar Registro")
    form.geometry("300x280")
    form.grab_set()

    e_site = ctk.CTkEntry(form, placeholder_text="Site")
    e_site.pack(pady=8)

    e_login = ctk.CTkEntry(form, placeholder_text="Login")
    e_login.pack(pady=8)

    e_senha = ctk.CTkEntry(form, placeholder_text="Senha")
    e_senha.pack(pady=8)

    def salvar():
        if not e_site.get() or not e_login.get() or not e_senha.get():
            messagebox.showwarning("Erro", "Preencha todos os campos")
            return

        cursor.execute(
            "INSERT INTO Geren (Site, Login, Senha) VALUES (?, ?, ?)",
            (e_site.get(), e_login.get(), e_senha.get())
        )
        conexao.commit()
        carregar_dados()
        form.destroy()

    ctk.CTkButton(form, text="Salvar", command=salvar).pack(pady=10)

def editar_registro():
    item = tabela.focus()
    if not item:
        messagebox.showwarning("Aviso", "Selecione um registro")
        return

    id_, site, login, senha = tabela.item(item)["values"]

    form = ctk.CTkToplevel(app)
    form.title("Editar Registro")
    form.geometry("300x280")
    form.grab_set()

    e_site = ctk.CTkEntry(form)
    e_site.insert(0, site)
    e_site.pack(pady=8)

    e_login = ctk.CTkEntry(form)
    e_login.insert(0, login)
    e_login.pack(pady=8)

    e_senha = ctk.CTkEntry(form)
    e_senha.insert(0, senha)
    e_senha.pack(pady=8)

    def salvar_edicao():
        cursor.execute("""
            UPDATE Geren
            SET Site=?, Login=?, Senha=?
            WHERE Id=?
        """, (e_site.get(), e_login.get(), e_senha.get(), id_))
        conexao.commit()
        carregar_dados()
        form.destroy()

    ctk.CTkButton(form, text="Salvar Alterações", command=salvar_edicao).pack(pady=10)

def excluir():
    item = tabela.focus()
    if not item:
        return

    id_ = tabela.item(item)["values"][0]

    if messagebox.askyesno("Confirmar", "Excluir este registro?"):
        if messagebox.askyesno("Confirmação Final", "Essa ação é irreversível. Continuar?"):
            cursor.execute("DELETE FROM Geren WHERE Id=?", (id_,))
            conexao.commit()
            carregar_dados()

# ----- Botões -----
ctk.CTkButton(frame_botao, text="Adicionar", command=abrir_formulario).pack(pady=10)
ctk.CTkButton(frame_botao, text="Editar", command=editar_registro).pack(pady=10)
ctk.CTkButton(frame_botao, text="Excluir", fg_color="red", command=excluir).pack(pady=10)

# =====================================================
# ================= GERADOR ===========================
# =====================================================
senha_var = ctk.StringVar()

frame_g = ctk.CTkFrame(aba_gerador)
frame_g.pack(pady=40)

ctk.CTkEntry(frame_g, width=300, textvariable=senha_var).pack(pady=10)

tam = ctk.IntVar(value=16)
ctk.CTkSlider(frame_g, from_=6, to=32, variable=tam).pack()

chk_up = ctk.BooleanVar(value=True)
chk_num = ctk.BooleanVar(value=True)
chk_sym = ctk.BooleanVar(value=True)

ctk.CTkCheckBox(frame_g, text="Maiúsculas", variable=chk_up).pack(anchor="w")
ctk.CTkCheckBox(frame_g, text="Números", variable=chk_num).pack(anchor="w")
ctk.CTkCheckBox(frame_g, text="Símbolos", variable=chk_sym).pack(anchor="w")

def gerar():
    chars = string.ascii_lowercase
    if chk_up.get(): chars += string.ascii_uppercase
    if chk_num.get(): chars += string.digits
    if chk_sym.get(): chars += "!@#$%&*?"
    senha_var.set("".join(random.choice(chars) for _ in range(tam.get())))

ctk.CTkButton(frame_g, text="Gerar Senha", command=gerar).pack(pady=10)

# =====================================================
# ================= CSV ===============================
# =====================================================
frame_csv = ctk.CTkFrame(aba_csv)
frame_csv.pack(pady=60)

def exportar_csv():
    caminho = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV", "*.csv")]
    )
    if not caminho:
        return

    cursor.execute("SELECT Site, Login, Senha FROM Geren")

    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "url", "username", "password", "note"])
        for site, login, senha in cursor.fetchall():
            writer.writerow([site, "", login, senha, ""])

    messagebox.showinfo("Sucesso", "CSV exportado com sucesso!")

def importar_csv():
    caminho = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
    if not caminho:
        return

    with open(caminho, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("name") and row.get("username") and row.get("password"):
                cursor.execute(
                    "INSERT INTO Geren (Site, Login, Senha) VALUES (?, ?, ?)",
                    (row["name"], row["username"], row["password"])
                )

    conexao.commit()
    carregar_dados()
    messagebox.showinfo("Sucesso", "CSV importado!")

ctk.CTkButton(frame_csv, text="Exportar CSV", command=exportar_csv).pack(pady=10)
ctk.CTkButton(frame_csv, text="Importar CSV", command=importar_csv).pack(pady=10)

# =====================================================
# ================= CONFIGURAÇÕES =====================
# =====================================================
frame_c = ctk.CTkFrame(aba_config)
frame_c.pack(pady=40)

ctk.CTkButton(frame_c, text="Modo Claro", command=lambda: ctk.set_appearance_mode("light")).pack(pady=5)
ctk.CTkButton(frame_c, text="Modo Escuro", command=lambda: ctk.set_appearance_mode("dark")).pack(pady=5)
btn_refresh_ids = ctk.CTkButton(
    frame_c,
    text="🔄 Reorganizar IDs",
    command=refresh_ids
)
btn_refresh_ids.pack(pady=5)


def limpar_banco():
    if not messagebox.askyesno("Atenção", "Apagar TODOS os dados?"):
        return

    win = ctk.CTkToplevel(app)
    win.title("Confirmação")
    win.geometry("300x180")
    win.grab_set()
    win.resizable(False, False)

    ctk.CTkLabel(win, text="Digite a senha para confirmar").pack(pady=(20, 10))

    senha_var = ctk.StringVar()
    entry_senha = ctk.CTkEntry(win, textvariable=senha_var, show="*")
    entry_senha.pack(pady=5, padx=30, fill="x")

    SENHA_CORRETA = "1234"  # <-----🔴 MUDE AQUI

    def confirmar():
        if senha_var.get() != SENHA_CORRETA:
            messagebox.showerror("Erro", "Senha incorreta!")
            return

        cursor.execute("DELETE FROM Geren")
        conexao.commit()
        carregar_dados()
        win.destroy()
        messagebox.showinfo("Sucesso", "Banco de dados limpo com sucesso!")

    ctk.CTkButton(win, text="Confirmar", fg_color="red", command=confirmar).pack(pady=15)


def confirmar_refresh():
    resposta = messagebox.askyesno(
        "Atenção",
        "Isso vai reorganizar TODOS os IDs.\n\nDeseja continuar?"
    )

    if resposta:
        refresh_ids()

ctk.CTkButton(frame_c, text="Limpar Banco de Dados", fg_color="red", command=limpar_banco).pack(pady=20)

# ================= FECHAR =================
def fechar():
    conexao.close()
    app.destroy()

app.protocol("WM_DELETE_WINDOW", fechar)
app.mainloop()