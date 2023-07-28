# Class Planner - Gerenciador de horários de aulas ![Badge](https://img.shields.io/static/v1?label=python&message=v3.10.9&color=lightblue&style=flat&logo=python)  ![Badge](https://img.shields.io/static/v1?label=django&message=v4.2.1&color=green&style=flat&logo=DJANGO)
 
<!-- <br />
<p align="center">
  <img src="https://github.com/ImFelippe365/lost-and-found/blob/main/static/svg/logo-colorful.svg" />
</p>
<br /> -->

API desenvolvida para armazenamento e controle dos dados das demais aplicações desenvolvidas.

Este projeto funciona juntamente com outras duas aplicações:
- [Class Planner Web](https://github.com/ImFelippe365/class-planner-web)
- [Class Planner Mobile](https://github.com/brunamariap/class-planner-mobile)

## ⚠️ Importante

Equipe: [Felippe Rian](https://github.com/ImFelippe365) & Bruna Maria

Projeto desenvolvido na disciplina de Desenvolvimento de Projetos II, utilizando os conhecimentos adquiridos nas demais, como Administração de Banco de Dados, Processo de Software, Arquitetura de Software e Desenvolvimento de Sistemas Distribuídos.

  
## Documentação

- [📄 Requisitos funcionais/não funcionais](https://docs.google.com/document/d/1W0PZumCOEnWrw8nvs900WqyFFRIyaeNj_PJDtZl1DhM/edit?usp=sharing)
- [👩🏻‍💻 Casos de uso](https://drive.google.com/file/d/1HHqFz7Sb1RquMtgSM0DuvqeMxMB2EQo3/view?usp=sharing)
- [🔗 Diagrama de classes](https://drive.google.com/file/d/1erp659dM3bxscE1tWZPmXEuS7V5sG7QI/view?usp=sharing)
- [⚙️ Visão funcional](https://drive.google.com/file/d/1HHqFz7Sb1RquMtgSM0DuvqeMxMB2EQo3/view?usp=sharing)
- [🔌 Visão de implantação](https://drive.google.com/file/d/1Re7xWZ-Pn726eTdb5cy-uro7NDB54fok/view)
- [🛠️ Visão de desenvolvimento](https://drive.google.com/file/d/1FxTzWoDgvyjRcIi4fNmS6tAe74MIEBfk/view?usp=sharing)
- [📚 C4 Context](https://drive.google.com/file/d/1q8C6XeyYlhlWZl0zyRHXCN54XjZHltkx/view?usp=sharing)
- [📚 C4 Container](https://drive.google.com/file/d/1pSIy8rnFrcqavpi9rYyxzk8V3EOXN_3S/view?usp=sharing)
- [📚 C4 Components](https://drive.google.com/file/d/14jmNeFA_Q00dZMZwj3luIi29YhQ7VAmJ/view?usp=sharing)
- [🖌️ Protótipo da interface (figma)](https://www.figma.com/file/2ugIt3gj5LtXetdSzGIfRO/Class-Planner?type=design&node-id=2%3A4&mode=design&t=p49KBSTQYvEmCpWY-1)

## Tecnologias utilizadas

- Django Rest Framework

## Instalação

Após clonar o repositório e criar um ambiente virtual, basta executar o comando abaixo para instalar as dependências do projeto.

```bash
pip install -r requirements.txt
```

Primeiro, é preciso configurar seu banco de dados criando um arquivo `.env` na pasta `config` do projeto.
Logo após, execute este comando para rodar as migrações no banco e gerar as tabelas.
```bash
py manage.py migrate
```

Por fim, para rodar o projeto, basta usar o comando a seguir
```bash
py manage.py runserver
```

Após isso, basta usufruir a API como desejar.
