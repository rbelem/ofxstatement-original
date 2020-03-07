Plugin para ofxstatement para converter arquivos CSV do Banco Original
==============================

Este é um plugin para [ofxstatement](https://github.com/kedder/ofxstatement) que
gera arquivos OFX a partir de arquivos CSV exportados pelo [Banco
Original](https://www.original.com.br).

Para instalar este plugin, faça o download ou clone o repositório e rode
o comando de instalação seguinte:

```
$ python3 setup.py install
```

Para converter os arquivos de extrato em formato CSV para OFX, rode o seguinte
comando:

```
$ ofxstatement convert -t original extrato.csv extrato.ofx
```
