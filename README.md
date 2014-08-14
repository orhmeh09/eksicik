# eksicik

eksisozluk.com gereçleri

##### Yapabilecekleri

- Bir başlıktaki tüm entryleri indirmek.

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
