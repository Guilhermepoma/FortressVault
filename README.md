# FortressVault 

**FortressVault** é uma aplicação desktop desenvolvida em **Python** para gerenciamento local de senhas, utilizando **CustomTkinter** para uma interface moderna e **SQLite** como banco de dados.

O foco do projeto é oferecer uma solução simples, rápida e visualmente agradável para cadastro, visualização e administração de informações de forma segura.

---

## Installation

Certifique-se de ter o **Python 3.10 ou superior** instalado.

Instale as dependências necessárias utilizando o **pip**:

```bash
pip install customtkinter pillow
```

> `tkinter` e `sqlite3` já vêm incluídos no Python e não precisam ser instalados separadamente.

---

## Usage

Execute a aplicação com o comando:

```bash
python FortressVault.py
```

A aplicação irá:

* Abrir uma interface gráfica moderna
* Conectar automaticamente ao banco de dados local (`db.db`)
* Permitir o gerenciamento dos registros cadastrados

Algumas ações sensíveis, como apagar todos os dados, exigem **confirmação por senha**.

---

## Features

* Interface moderna com **CustomTkinter**
* Banco de dados local com **SQLite**
* Confirmação de segurança para ações críticas
* Atualização automática da interface

---

## Contributing

Pull requests são bem-vindos.

Para mudanças maiores:

* Abra uma *issue* primeiro para discussão
* Mantenha o código organizado e documentado

---

## License

Este projeto está sob a licença **MIT**.

[MIT](https://choosealicense.com/licenses/mit/)
