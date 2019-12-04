#!/usr/bin/python
# -*- coding: utf-8 -*-
#===============================================================================#
#            Academico - Ferramenta de pesquisa de produção científica          #
#                    (C) 2015 by Mauro J. Cavalcanti                            #
#                         <maurobio@gmail.com>                                  #
#                                                                               #
#  Este programa é software livre; você pode redistribuí-lo e/ou                #
#  modificá-lo sob os termos da Licença Pública Geral GNU, conforme             #
#  publicada pela Free Software Foundation; tanto a versão 2 da                 #
#  Licença como (a seu critério) qualquer versão mais nova.                     #
#                                                                               #
#  Este programa é distribuído na expectativa de ser útil, mas SEM              #
#  QUALQUER GARANTIA; sem mesmo a garantia implícita de                         #
#  COMERCIALIZAÇÃO ou de ADEQUAÇÃO A QUALQUER PROPÓSITO EM                      #
#  PARTICULAR. Consulte a Licença Pública Geral GNU para obter mais             #
#  detalhes.                                                                    #
#                                                                               #
#  Dependências:                                                                #
#    Python 2.7+ (http://www.python.org)                                        #
#    PyQt 4.8+ (http://www.riverbankcomputing.com/software/pyqt)                #
#    BeautifulSoup 4.3+ (www.crummy.com/software/BeautifulSoup)                 #
#    NumPy 1.4+ (http://www.numpy.org)                                          #
#    Matplotlib 0.98+ (http://www.matplotlib.org)                               #
#                                                                               #
#  HISTÓRICO DE REVISÕES                                                        #
#    Versão 1.00, 07 Maio 15 - Primeira versão                                  #
#    Versão 1.10, 08 Maio 15 - Segunda versão                                   #
#    Versã9 1.20, 12 Maio 15 - Terceira versão                                  #
#    Versão 1.30, 03 Novembro 15 - Quarta versão                                #
#    Versão 1.40, 16 Novembro 15 - Quinta versão                                #
#    Versão 1.50, 19 Novembro 15 - Sexta versão                                 #
#    Versão 1.60, 20 Novembro 15 - Sétima versão                                #
#    Versão 1.70, 25 Novembro 15 - Oitava versão                                #
#===============================================================================#

import os, sys, time, string, platform, formatter, collections, random, re, glob, sqlite3
import urllib, urllib2, httplib, htmllib, webbrowser
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import bs4
from bs4 import BeautifulSoup
from PyQt4 import QtCore, QtGui, QtWebKit
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QCursor
from PyQt4.QtCore import QT_VERSION_STR
from PyQt4.Qt import PYQT_VERSION_STR
from htmlentitydefs import codepoint2name
from unicodedata import normalize

import resources

__version__ = "1.7.0"

def remover_acentos(txt, codif="utf-8"):
    return normalize("NFKD", txt.decode(codif)).encode("ASCII","ignore")

def htmlescape(text):
    text = (text).decode("utf-8")
    d = dict((unichr(code), u'&%s;' % name) for code,name in codepoint2name.iteritems() if code!=38)
    if u"&" in text:
        text = text.replace(u"&", u"&amp;")
    for key, value in d.iteritems():
        if key in text:
            text = text.replace(key, value)
    return text

def messagederreur(msgtyp, msg):
    """permet d'afficher ou non dans la console les messages d'erreur de Qt
       mise en place par: QtCore.qInstallMsgHandler(messagederreur)
    """
    if msgtyp == QtCore.QtDebugMsg:
        print("Debug: %s\n" % (msg,))

    elif msgtyp == QtCore.QtWarningMsg:
        # exemple de désactivation d'un message donné par QWebKit.QWebView
        if msg != "QFont::setPixelSize: Pixel size <= 0 (0)":
            print("Warning: %s\n" % (msg,))

    elif msgtyp == QtCore.QtCriticalMsg:
        print("Critical: %s\n" % (msg,))

    elif msgtyp == QtCore.QtFatalMsg:
        print("Fatal: %s\n" % (msg))
        sys.exit()

def we_are_frozen():
    """Returns whether we are frozen via py2exe.
    This will affect how we find out where we are located."""
    return hasattr(sys, "frozen")

def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""
    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

class Parser(htmllib.HTMLParser):
    """" build a list of tuples (anchor text, URL) """
    def __init__(self, verbose=0):
        self.anchors = []
        f = formatter.NullFormatter()
        htmllib.HTMLParser.__init__(self, f, verbose)

    def anchor_bgn(self, href, name, type):
        self.save_bgn()
        self.href = href
        self.name = name
        self.type = type

    def anchor_end(self):
        text = string.strip(self.save_end())
        if self.href and text:
            self.anchors.append( (text, self.href) )

class AppURLopener(urllib.FancyURLopener):
    # trick Google into thinking I'm using Firefox
    version = "Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11"

urllib._urlopener = AppURLopener()

class GoogleScholar:
    """ Search Google Scholar """
    def __init__(self, searchStr, limit=10):
        self.SCHOLAR_URL = "http://www.scholar.google.com/scholar"
        self.searchStr = searchStr
        self.limit = limit

    def getCitations(self):
        """Search Google Scholar for articles and publications containing terms of interest"""
        self.searchStr = '"' + self.searchStr.replace(' ', '+') + '"'
        try:
            file = urllib.urlopen(self.SCHOLAR_URL + "?q=%s&ie=UTF-8&oe=UTF-8&hl=pt-BR&btnG=Search" % self.searchStr)
            html = file.read()
            file.close()
            p = Parser()
            p.feed(html)
            p.close()
            candidates = {}
            count = 0
            for text, url in p.anchors:
                if count < self.limit:
                    i = url.find("http")
                    if i == 0:
                        j = url.find("google.com")
                        if j == -1:
                            k = url.find("answers.com")
                            if k == -1:
                                l = url.find("direct.bl.uk")
                                if l == -1:
                                    candidates[url] = text
                                    count += 1

            # Sleep for one second to prevent IP blocking from Google
            time.sleep(1)
        except:
            candidates = {}
        return candidates

class Lattes:
    """ Parse Lattes Platform file """
    def __init__(self, filename):
        self.filename = unicode(filename, "latin-1", errors="ignore")
        self.soup = BeautifulSoup(open(self.filename))
        text = self.soup.get_text()
        outfile = open("temp.txt", "wb")
        outfile.write(text.encode("utf-8", "ignore"))
        outfile.close()

    #def __del__(self):
    #    if os.path.exists("temp.txt"):
    #        os.remove("temp.txt")

    def getName(self):
        s = self.soup.title.string.encode("utf-8", "ignore")
        name = s[s.find("(")+1:s.find(")")]
        return name

    def getArticles(self):
        articles = self.soup.findAll(attrs={"class": "artigo-completo"})
        lines = [article.get_text(separator="|") for article in articles]
        return lines

    def getChapters(self):
        chapters = []
        with open("temp.txt", "rb") as infile:
            while True:
                line = infile.readline()
                if not line: break
                if line.startswith("Capítulos"):
                    while True:
                        text = infile.readline()
                        if text.startswith("Textos"): break
                        if text == '\n': continue
                        if text.strip('. \n').isdigit(): continue
                        chapters.append(text.strip('\n'))
        return chapters

    def getTexts(self):
        texts = []
        with open("temp.txt", "rb") as infile:
            while True:
                line = infile.readline()
                if not line: break
                if line.find("/revistas") != -1:
                    while True:
                        text = infile.readline()
                        if text.startswith("Resumos"): break
                        if text == '\n': continue
                        if text.strip('. \n').isdigit(): continue
                        texts.append(text.strip('\n'))
        return texts

    def getAbstracts(self):
        abstracts = []
        with open("temp.txt", "rb") as infile:
            while True:
                line = infile.readline()
                if not line: break
                if line.startswith("Resumos"):
                    while True:
                        text = infile.readline()
                        if text.startswith("Apresentações"): break
                        if text.find("Resumos publicados em anais de congressos") != -1: continue
                        if text == '\n': continue
                        if text.strip('. \n').isdigit(): continue
                        abstracts.append(text.strip('\n'))
        return abstracts

class Browser(QtGui.QMainWindow):
    def __init__(self):
        """ Initialize the browser GUI and connect the events """

        QtGui.QMainWindow.__init__(self)
        self.centralwidget = QtGui.QWidget(self)

        self.mainLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setMargin(1)

        self.frame = QtGui.QFrame(self.centralwidget)

        self.gridLayout = QtGui.QVBoxLayout(self.frame)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)

        self.horizontalLayout = QtGui.QHBoxLayout()
        self.lbl_find = QtGui.QLabel(u" Pasta de Currículos: ")
        self.edt_find = QtGui.QLineEdit(self.frame)
        self.edt_find.setReadOnly(True)
        self.btn_search = QtGui.QPushButton("&Pesquisar", self.frame)
        self.btn_help = QtGui.QPushButton(self.frame)
        self.btn_help.setFlat(True)
        self.btn_help.setIcon(QtGui.QIcon(":/help.png"))
        self.btn_help.setToolTip(u"Obter ajuda")
        self.btn_about = QtGui.QPushButton(self.frame)
        self.btn_about.setFlat(True)
        self.btn_about.setIcon(QtGui.QIcon(":/about.png"))
        self.btn_about.setToolTip(u"Exibir informação sobre o sistema")
        self.btn_refresh = QtGui.QPushButton(self.frame)
        self.btn_refresh.setFlat(True)
        self.btn_refresh.setIcon(QtGui.QIcon(":/refresh.png"))
        self.btn_refresh.setToolTip(u"Atualizar a página de resultados")
        self.btn_refresh.setEnabled(False)
        self.btn_exit = QtGui.QPushButton(self.frame)
        self.btn_exit.setFlat(True)
        self.btn_exit.setIcon(QtGui.QIcon(":/exit.png"))
        self.btn_exit.setToolTip("Terminar o programa")

        self.horizontalLayout.addWidget(self.lbl_find)
        self.horizontalLayout.addWidget(self.edt_find)
        self.horizontalLayout.addWidget(self.btn_search)
        self.horizontalLayout.addWidget(self.btn_refresh)
        self.horizontalLayout.addWidget(self.btn_help)
        self.horizontalLayout.addWidget(self.btn_about)
        self.horizontalLayout.addWidget(self.btn_exit)
        self.gridLayout.addLayout(self.horizontalLayout)

        self.browser = QtWebKit.QWebView()
        self.browser.setContextMenuPolicy(Qt.NoContextMenu)

        self.gridLayout.addWidget(self.browser)
        self.mainLayout.addWidget(self.frame)
        self.setCentralWidget(self.centralwidget)
        self.setGeometry(192, 107, 766, 441)
        self.setWindowTitle(u"Acadêmico")
        self.setWindowIcon(QtGui.QIcon(":/schlfish.png"))

        shortcut = QtGui.QShortcut(QtGui.QKeySequence("F1"), self)
        shortcut.activated.connect(self.help)
        self.connect(self.btn_search, QtCore.SIGNAL("clicked()"), self.find)
        self.connect(self.btn_refresh, QtCore.SIGNAL("clicked()"), self.refresh)
        self.connect(self.btn_about, QtCore.SIGNAL("clicked()"), self.about)
        self.connect(self.btn_help, QtCore.SIGNAL("clicked()"), self.help)
        self.connect(self.btn_exit, QtCore.SIGNAL("clicked()"), self.close)
        self.connect(self.browser, QtCore.SIGNAL("linkClicked (const QUrl&)"), self.linkClicked)
        self.statusBar().showMessage("Pronto")
        self.show()

    def linkClicked(self, url):
        webbrowser.open_new_tab(str(url.toString()))

    def load(self):
        stream = QtCore.QFile("data/Resultados.htm")
        if stream.open(QtCore.QFile.ReadOnly):
           html = QtCore.QString.fromUtf8(stream.readAll())
        stream.close()
        try:
            approot = os.path.abspath(os.path.dirname(__file__))
        except NameError:  # We are the main py2exe script, not a module
            approot = os.path.abspath(os.path.dirname(sys.argv[0]))
        baseUrl = QtCore.QUrl.fromLocalFile(os.path.join(approot, "data/"))
        self.browser.setHtml(html, baseUrl)
        self.browser.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateExternalLinks)

    def find(self):
        directory = QtGui.QFileDialog.getExistingDirectory(self, u"Pasta de Currículos")
        if not directory.isEmpty():
            self.edt_find.setText(directory)
        else:
            return
        if self.search(directory):
            self.load()
            self.btn_refresh.setEnabled(True)

    def about(self):
        QtGui.QMessageBox.about(self, u"Sobre o Acadêmico",
        u"""<b>Acadêmico</b> v. %s
        <p>Ferramenta de análise de produção acadêmica.
        <p>Extração e análise de dados acadêmicos da Plataforma Lattes/CNPq e do Google Scholar.
        <p>&copy; 2015 Mauro J. Cavalcanti
        <p>Python: %s
        <br>Qt: %s
        <br>PyQt: %s
        <br>SQLite: %s
        <br>PySQLite %s
        <br>Platforma: %s %s""" % (__version__, platform.python_version(),
        QT_VERSION_STR, PYQT_VERSION_STR, sqlite3.sqlite_version, sqlite3.version, platform.system(), platform.release()))

    def refresh(self):
        self.load(self.filename)

    def help(self):
        stream = QtCore.QFile("help/index.html")
        if stream.open(QtCore.QFile.ReadOnly):
           html = QtCore.QString.fromLatin1(stream.readAll())
        stream.close()
        try:
            approot = os.path.abspath(os.path.dirname(__file__))
        except NameError:  # We are the main py2exe script, not a module
            approot = os.path.abspath(os.path.dirname(sys.argv[0]))
        baseUrl = QtCore.QUrl.fromLocalFile(os.path.join(approot, "help/"))
        self.browser.setHtml(html, baseUrl)

    def closeEvent(self, event):
        quit_msg = "Deseja encerrar o programa?"
        reply = QtGui.QMessageBox.question(self, u"Confirmação",
            quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def search(self, path):
        stylesheet = """<style type="text/css" media="all">\n
        <!--\n
        body, table {
            background: white none repeat scroll 0%;
            color: black;
            font-family: Verdana,Helvetica,Arial,sans-serif;
        }
        body, table {
            font-size: 83%;
        }
        body table {
            font-size: 100%;
        }
        a:link {
            background: transparent none repeat scroll 0%;
            color: #008080;
        }
        a:visited {
            background: transparent none repeat scroll 0%;
            color: #008080;
        }
        a:active {
            background: transparent none repeat scroll 0%;
            color: #008080;
        }
        a:hover {
            background: #d7e0f7 none repeat scroll 0%;
            color: #008080;
        }
        h1, h2, h3, h4, h5, h6 {
            background: transparent none repeat scroll 0%;
            text-align: left;
            margin-top: 1em;
            margin-bottom: 0.6em;
            font-family: Arial,Helvetica,sans-serif;
            font-weight: bold;
            font-size: 1em;
        }
        h1 {
            font-size: 160%;
            color: #0c0ca4;
        }
        h2 {
            font-size: 145%;
            color: #0c0ca4;
        }
        h3 {
            font-size: 125%;
            color: #0c0ca4;
        }
        h4 {
            font-size: 115%;
            color: #0c0ca4;
        }
        h5, h6 {
            font-size: 100%;
        }
        div, th, td, form, input, textarea, select {
            font-family: Verdana,Arial,Helvetica,sans-serif;
        }
        p, ul, ol, li, dl, address, blockquote {
            font-family: Verdana,Arial,Helvetica,sans-serif;
            margin-top: 0.7em;
            margin-bottom: 0.7em;
            font-size: 11px
        }
        ul, ol {
            margin-left: 0.1em;
        }
        ul.compact li, ol.compact li, ol.compact li p {
            margin-top: 0;
            margin-bottom: 0;
        }
        ul.separated li, ol.separated li {
            margin-top: 0.7em;
            margin-bottom: 0.7em;
        }
        \n
        -->\n
        </style>\n"""

        filenames = glob.glob(str(path) + '/' + "*.htm")
        if len(filenames) == 0:
            QtGui.QMessageBox.warning(self, u"Aviso",
                    u"A pasta selecionada não contém arquivos de currículos")
            return False

        if not os.path.exists("data/"):
            os.makedirs("data/")

        db = sqlite3.connect("data/academico.db")
        cursor = db.cursor()
        cursor.execute("DROP TABLE IF EXISTS Stats")
        cursor.execute("CREATE TABLE Stats(Id INT, Name TEXT, Articles INT, Chapters INT, Texts INT, Abstracts INT, Citations INT)")
        db.commit()

        msgbox = QtGui.QMessageBox(parent=self)
        msgbox.setWindowIcon(QtGui.QIcon(":/schlfish.png"))
        msgbox.setIcon(QtGui.QMessageBox.Question)
        msgbox.setWindowTitle(u"Opções de Saída")
        msgbox.setText(u"Selecione o tipo de relatório:")
        summaryButton = QtGui.QPushButton(u"Relatório Resumido")
        completeButton = QtGui.QPushButton(u"Relatório Detalhado")
        cancelButton = QtGui.QPushButton(u"Cancelar")
        msgbox.addButton(summaryButton, QtGui.QMessageBox.ActionRole)
        msgbox.addButton(completeButton, QtGui.QMessageBox.ActionRole)
        msgbox.addButton(cancelButton, QtGui.QMessageBox.RejectRole)
        msgbox.exec_()
        if msgbox.clickedButton() == summaryButton:
            full_report = False
        elif msgbox.clickedButton() == completeButton:
            full_report = True
        elif msgbox.clickedButton() == cancelButton:
            return

        filename = "Resultados.htm"
        outfile = open("data/" + filename, "wb")
        outfile.write("<html>\n")
        outfile.write("<head>\n")
        outfile.write(stylesheet)
        outfile.write("</head>\n")
        outfile.write("<body bgcolor="'#ffffff'">\n")

        # Begin file processing loop
        id = 0
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        for filename in filenames:
            self.statusBar().showMessage(u"Processando currículo... " + QtCore.QString(os.path.basename(filename)))
            lattes = Lattes(filename)
            name = lattes.getName()

            if full_report:
                outfile.write("<hr>\n")
                outfile.write("<h2>" + htmlescape("Produção bibliográfica de ") + htmlescape(name) + "</h2>\n")

            values = []
            if full_report:
                outfile.write("<h3>" + htmlescape("Artigos completos publicados em periódicos") + "</h3>\n")
            articles = lattes.getArticles()
            narticles = len(articles)
            values.append(narticles)
            if full_report:
                if narticles == 0:
                    outfile.write("Nenhum artigo encontrado\n")
                else:
                    outfile.write("<ol>\n")
                    for i in range(narticles):
                        article = articles[i].encode("utf8", "ignore")
                        article = article.replace("\n", "")
                        outfile.write("<li>")
                        outfile.write(article.split('|')[10] + article.split('|')[11] +  \
                            article.split('|')[12] + article.split('|')[13] + article.split('|')[14])
                        try:
                            outfile.write(article.split('|')[15] + article.split('|')[16])
                        except IndexError:
                            continue
                        outfile.write("</li>\n")
                    outfile.write("</ol>\n")

            if full_report:
                outfile.write("<h3>" + htmlescape("Livros e capítulos") + "</h3>\n")
            chapters = lattes.getChapters()
            nchapters = len(chapters)
            values.append(nchapters)
            if full_report:
                if nchapters == 0:
                    outfile.write(htmlescape("Nenhum livro ou capítulo encontrado\n"))
                else:
                    outfile.write("<ol>\n")
                    for chapter in chapters:
                        outfile.write("<li>"+ chapter + "</li>\n")
                    outfile.write("</ol>\n")

            if full_report:
                outfile.write("<h3>" + htmlescape("Textos em jornais ou revistas (magazine)") + "</h3>\n")
            texts = lattes.getTexts()
            ntexts = len(texts)
            values.append(ntexts)
            if full_report:
                if ntexts == 0:
                    outfile.write("Nenhum texto encontrado\n")
                else:
                    outfile.write("<ol>\n")
                    for text in texts:
                        outfile.write("<li>"+ text + "</li>\n")
                    outfile.write("</ol>\n")

            if full_report:
                outfile.write("<h3>" + htmlescape("Resumos publicados em anais de congressos") + "</h3>\n")
            abstracts = lattes.getAbstracts()
            nabstracts = len(abstracts)
            values.append(nabstracts)
            if nabstracts == 0 and full_report:
                outfile.write("Nenhum resumo encontrado\n")
            else:
                if full_report:
                    outfile.write("<ol>\n")
                    for abstract in abstracts:
                        outfile.write("<li>"+ abstract + "</li>\n")
                    outfile.write("</ol>\n")

            if full_report:
                outfile.write("<h3>" + htmlescape("Citações no Google Acadêmico") + "</h3>\n")
            scholar = GoogleScholar(name)
            pubs = scholar.getCitations()
            npubs = len(pubs)
            values.append(npubs)
            if full_report:
                if npubs == 0:
                    outfile.write("Nenhuma citação encontrada\n")
                else:
                    for pub in pubs.keys():
                        outfile.write("<hr noshade>\n")
                        outfile.write("<b><a href='" + pub + "'>" + pubs[pub] + "</a></b><br>\n")

            if full_report:
                outfile.write("<hr>\n")
                outfile.write("<h3>" + htmlescape("Totais de Produção Bibliográfica de ") + htmlescape(name) + "</h3>\n")
                outfile.write("<table border='1' width='100%'>\n")
                outfile.write("<tr>\n")
                outfile.write("<td>" + htmlescape("Artigos completos publicados em periódicos") + "</td>\n")
                outfile.write("<td align=""right"">" + str(narticles) + "</td>\n")
                outfile.write("</tr>\n")
                outfile.write("<tr>\n")
                outfile.write("<td>" + htmlescape("Capítulos de livros publicados") + "</td>\n")
                outfile.write("<td align=""right"">" + str(nchapters) + "</td>\n")
                outfile.write("</tr>\n")
                outfile.write("<tr>\n")
                outfile.write("<td>" + htmlescape("Textos em jornais ou revistas (magazine)") + "</td>\n")
                outfile.write("<td align=""right"">" + str(ntexts) + "</td>\n")
                outfile.write("</tr>\n")
                outfile.write("<tr>\n")
                outfile.write("<td>" + htmlescape("Resumos publicados em anais de eventos") + "</td>\n")
                outfile.write("<td align=""right"">" + str(nabstracts) + "</td>\n")
                outfile.write("</tr>\n")
                outfile.write("<td>" + htmlescape("Citações no Google Acadêmico") + "</td>\n")
                outfile.write("<td align=""right"">" + str(npubs) + "</td>\n")
                outfile.write("</tr>\n")
                outfile.write("</table>\n")

                keys = ["Artigos", u"Capítulos", "Textos", "Resumos", u"Citações"]
                data = dict(zip(keys, values))
                n = len(data)
                x = np.arange(1, n + 1)
                y = [num for (s, num) in data.items()]
                labels = [s for (s, num) in data.items()]
                width = 0.75
                clist = random.sample(colors.cnames, n)
                plt.clf()
                figf = os.path.splitext(os.path.basename(filename))[0] + ".png"
                plt.bar(x, y, width, color=clist)
                plt.title(u"PRODUÇÃO BIBLIOGRÁFICA POR CATEGORIA")
                plt.xlabel("CATEGORIAS")
                plt.ylabel(u"NÚMERO DE TRABALHOS")
                plt.xticks(x + width / 2.0, labels, fontsize=10)
                plt.grid(False)
                plt.savefig("data/" + figf, dpi=100)
                outfile.write("<img src='" + figf.decode("latin-1").encode("utf-8") + "'>\n")

            cursor.execute("INSERT INTO Stats(id, name, articles, chapters, texts, abstracts, citations)\
                            VALUES(?,?,?,?,?,?,?)", (id + 1, remover_acentos(name), narticles, nchapters, ntexts, nabstracts, npubs))
            db.commit()
            id += 1

        # End file processing loop
        cursor.execute("SELECT SUM(Articles), SUM(Chapters), SUM(Texts), SUM(Abstracts), SUM(Citations)\
                        FROM Stats")
        result = cursor.fetchall()

        outfile.write("<hr>\n")
        outfile.write("<h3>" + htmlescape("Totais de Produção Bibliográfica da Pasta ") + str(path) + \
            " - " + str(id) + htmlescape(" currículo(s) analisado(s)") + "</h3>\n")
        outfile.write("<table border='1' width='100%'>\n")
        outfile.write("<tr>\n")
        outfile.write("<td>" + htmlescape("Artigos completos publicados em periódicos") + "</td>\n")
        outfile.write("<td align=""right"">" + str(result[0][0]) + "</td>\n")
        outfile.write("</tr>\n")
        outfile.write("<tr>\n")
        outfile.write("<td>" + htmlescape("Capítulos de livros publicados") + "</td>\n")
        outfile.write("<td align=""right"">" + str(result[0][1]) + "</td>\n")
        outfile.write("</tr>\n")
        outfile.write("<tr>\n")
        outfile.write("<td>" + htmlescape("Textos em jornais ou revistas (magazine)") + "</td>\n")
        outfile.write("<td align=""right"">" + str(result[0][2]) + "</td>\n")
        outfile.write("</tr>\n")
        outfile.write("<tr>\n")
        outfile.write("<td>" + htmlescape("Resumos publicados em anais de eventos") + "</td>\n")
        outfile.write("<td align=""right"">" + str(result[0][3]) + "</td>\n")
        outfile.write("</tr>\n")
        outfile.write("<td>" + htmlescape("Citações no Google Acadêmico") + "</td>\n")
        outfile.write("<td align=""right"">" + str(result[0][4]) + "</td>\n")
        outfile.write("</tr>\n")
        outfile.write("</table>\n")

        values = list(result[0])
        keys = ["Artigos", u"Capítulos", "Textos", "Resumos", u"Citações"]
        data = dict(zip(keys, values))
        n = len(data)
        x = np.arange(1, n + 1)
        y = [num for (s, num) in data.items()]
        labels = [s for (s, num) in data.items()]
        width = 0.75
        clist = random.sample(colors.cnames, n)
        plt.clf()
        figf = "Resultados.png"
        plt.bar(x, y, width, color=clist)
        plt.title(u"PRODUÇÃO BIBLIOGRÁFICA POR CATEGORIA")
        plt.xlabel("CATEGORIAS")
        plt.ylabel(u"NÚMERO DE TRABALHOS")
        plt.xticks(x + width / 2.0, labels, fontsize=10)
        plt.grid(False)
        plt.savefig("data/" + figf, dpi=100)
        outfile.write("<img src='" + figf + "'>\n")

        self.statusBar().showMessage("Pronto")
        QtGui.QApplication.restoreOverrideCursor()
        outfile.write("<hr>\n")
        outfile.write("<p><i>Gerado em " + time.strftime("%d/%m/%Y", time.localtime()) + " as " + time.strftime("%H:%M:%S", time.localtime()) + " ")
        outfile.write("pelo sistema <b>" + htmlescape("Acadêmico") +"</b> v. " + __version__ + ". ")
        outfile.write(htmlescape("Resultados sujeitos a falhas devido a inconsistências no preenchimento dos currículos Lattes.") + "</i></p>\n")
        outfile.write("</body>\n")
        outfile.write("</html>\n")
        outfile.close()

        if os.path.exists("temp.txt"):
            os.remove("temp.txt")

        db.close()
        return True

if __name__ == "__main__":
    QtCore.qInstallMsgHandler(messagederreur)
    app = QtGui.QApplication(sys.argv)
    main = Browser()
    sys.exit(app.exec_())