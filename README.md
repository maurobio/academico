# <img src="images\schlfish.jpg" alt="schlfish" style="zoom:50%;" /> Acadêmico

Ferramenta de software para extração semiautomática, compilação e análise de dados de produção bibliográfica acadêmica a partir da Plataforma Lattes/CNPq.

### Sobre

***O Acadêmico*** é uma ferramenta de software desenvolvida com a linguagem de programação [Python](http://www.python.org/), para extração semiautomática, compilação e análise de dados de produção bibliográfica acadêmica a partir da [Plataforma Lattes/CNPq](http://lattes.cnpq.br/).

O principal objetivo do ***Acadêmico*** é facilitar a compilação e quantificação da produção bibliográfica de um grupo de pesquisadores cadastrados na [Plataforma Lattes/CNPq](http://lattes.cnpq.br/) (por exemplo, um grupo de pesquisa, um curso de pós-graduação ou um departamento acadêmico). Os relatórios gerados possibilitam uma avaliação rápida da produção do grupo de interesse.

***O Acadêmico*** é similar ao [scriptLattes](http://scriptlattes.sourceforge.net/), com algumas diferenças fundamentais:

- ***O Acadêmico*** extrai e analisa apenas dados de produção bibliográfica; dados de produções técnicas, artísticas, orientações, projetos de pesquisa, prêmios e títulos não são considerados.
- ***O Acadêmico*** não gera grafos de colaborações nem mapas de geolocalização.
- ***O Acadêmico*** procura e extrai automaticamente citações bibliográficas do [Google Acadêmico](http://scholar.google.com/), para cada membro do grupo de interesse.
- ***O Acadêmico*** é amigável, com uma interface gráfica de usuário fácil de instalar e de utilizar; não requer arquivos de configuração nem arquivos de listas de identificadores do Lattes.

### Tutorial

[Tutorial para utilização do ***Acadêmico***](http://oacademico.sourceforge.net/help/index.html)

### Download

***O Acadêmico*** (incluindo programa de instalação para MS-Windows XP, Vista, 7, 8, 10 e código-fonte em Python) está disponível para download no repositório [SourceForge](http://sourceforge.net/projects/oacademico/).

O pacote de instalação inclui o interpretador Python e todos os módulos necessários à execução do programa.

Para executar o programa a partir do código-fonte, é necessário instalar as seguintes dependências:

- [Python](http://www.python.org) 2.7+ 
- [PyQt](http://www.riverbankcomputing.com/software/pyqt) 4.8+
- [BeautifulSoup](http://oacademico.sourceforge.net/www.crummy.com/software/BeautifulSoup) 4.3+ 
- [NumPy](http://www.numpy.org/) 1.4+
- [Matplotlib](http://www.matplotlib.org/) 0.98+ 

### Licença

***O Acadêmico*** é software livre e de código aberto, distribuído nos termos da [Licença Pública Geral GNU](http://www.magnux.org/doc/GPL-pt_BR.txt) (GNU GPL), versão 2 ou posterior.
