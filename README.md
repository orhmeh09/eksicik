# eksicik

eksisozluk.com gereçleri: **web arayüzü için API + betik**

##### Neler Neler...

- Esnek Python API'ı.
- Kısa kullanım için [filtre program](https://en.wikipedia.org/wiki/Filter_(software)) betiği.
- Popüler veya bugün gibi listelerdeki başlıkları indirme.
- Bir başlıktaki tüm entryleri indirme.
- JSON veya XML ciktisi verme.

##### Gerekli Paketler

- bs4 (Beautiful Soup 4)

##### İndirme

    git clone https://github.com/nrs/eksicik

##### Sisteme Kurmadan Deneme

Komutlar (yani `build/scripts` dizini) Python sürümünüze göre değişebilir.

    cd eksicik
    export PYTHONPATH=$PYTHONPATH:$PWD/build/lib/
    python setup.py build
    ./build/scripts-2.7/eksicik

##### Kurulum

Sisteminize kurabilmeniz için root olmanız gerekmektedir.

    cd eksicik
    sudo python setup.py install

##### Çalıştırma

Yardımı göstermek için `eksicik` betiğini argümansız çalıştırın.

    $ eksicik
    usage: eksicik [-h] [-b BASLIK] [-o OUTPUT_FILE]

    optional arguments:
      -h, --help            show this help message and exit
    ....
