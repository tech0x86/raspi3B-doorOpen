# raspi3B-doorOpen

# はじめに
備忘録用

## どんなもの？

宅急便を置き配してもらうために、自動でエントランスのドアを開錠してもらうシステム

## 全体の流れ

1、配達業者がきてエントランスで部屋の呼び出しボタンを押す

2、部屋にある受話器のランプが点灯

3、システムがランプを検知

4、受話器をあげて、開錠ボタンを押す

5、配達業者が玄関前まで来て置き配してくれる

#システムの流れ
1、無限ループで光センサーの検知を待機

2、光を検知したら受話器のサーボを動かす
2、光を検知したら受話器のサーボを動かす



#環境

## Raspberry Pi 3Bプラス　
rasbian OS

## 電子工作
動作チェック用LED

5V2A　電源

光センサー：Cdセンサー【I-00110】　ＣｄＳセル　５ｍｍタイプ

サーボモータx2： マイクロサーボ９ｇ　ＳＧ－９０
（動作中以外電源を切らないとノイズのせいでモータが常に微妙に動作しているので、トランジスタで電源を遮断）

スイッチングトランジスタ：ＰｃｈパワーＭＯＳＦＥＴ　６０Ｖ５Ａ　２ＳＪ６８１

半固定　抵抗　（10kオームだった気がする

細かいもの諸々

システム全体像
![IMG_3706](https://user-images.githubusercontent.com/6120427/156879679-da268966-5f8a-47c9-a15a-58eaf0c3ce3a.jpeg)


接写　いろんなアングルから

![IMG_3707](https://user-images.githubusercontent.com/6120427/156879683-bb73f3b1-6f03-4312-aa8c-733be9bbc29c.jpeg)
![IMG_3709](https://user-images.githubusercontent.com/6120427/156879688-0102baad-dccd-45f4-9de5-54c531dc4c36.jpeg)


#環境設定

##IP固定
/etc/dhcpcd.conf
interface wlan0
static ip_address=192.168.0.2/24
static routers=192.168.0.1

##定期起動
cron:システム起動時に自動でpythonファイルを実行
（ここのファイルでいいかちょっと怪しい）

/var/spool/cron/crontabs/pi

以下を追記

@reboot python /var/samba/mac/main.py

# ファイル位置
/var/samba/mac/main.py

#その他
hostname: raspi

##ssh接続

pi@192.168.0.2

##gpio　設定

$gpio readall

<img width="614" alt="スクリーンショット 2022-03-05 19 27 51" src="https://user-images.githubusercontent.com/6120427/156879336-46abe367-89d6-4993-b3b8-4e46c8bf1edf.png">

 +-----+-----+---------+------+---+---Pi 3B+-+---+------+---------+-----+-----+
 | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 |     |     |    3.3v |      |   |  1 || 2  |   |      | 5v      |     |     |
 |   2 |   8 |   SDA.1 | ALT0 | 1 |  3 || 4  |   |      | 5v      |     |     |
 |   3 |   9 |   SCL.1 | ALT0 | 1 |  5 || 6  |   |      | 0v      |     |     |
 |   4 |   7 | GPIO. 7 |   IN | 0 |  7 || 8  | 1 | ALT5 | TxD     | 15  | 14  |
 |     |     |      0v |      |   |  9 || 10 | 1 | ALT5 | RxD     | 16  | 15  |
 |  17 |   0 | GPIO. 0 |   IN | 0 | 11 || 12 | 0 | IN   | GPIO. 1 | 1   | 18  |
 |  27 |   2 | GPIO. 2 |   IN | 0 | 13 || 14 |   |      | 0v      |     |     |
 |  22 |   3 | GPIO. 3 |   IN | 0 | 15 || 16 | 0 | IN   | GPIO. 4 | 4   | 23  |
 |     |     |    3.3v |      |   | 17 || 18 | 0 | IN   | GPIO. 5 | 5   | 24  |
 |  10 |  12 |    MOSI | ALT0 | 0 | 19 || 20 |   |      | 0v      |     |     |
 |   9 |  13 |    MISO | ALT0 | 0 | 21 || 22 | 0 | IN   | GPIO. 6 | 6   | 25  |
 |  11 |  14 |    SCLK | ALT0 | 0 | 23 || 24 | 1 | OUT  | C![IMG_3709](https://user-images.githubusercontent.com/6120427/156879692-c6843ce2-73ff-4d1b-8062-b9fa2bc08a08.jpeg)
E0     | 10  | 8   |
 |     |     |      0v |      |   | 25 || 26 | 1 | OUT  | CE1     | 11  | 7   |
 |   0 |  30 |   SDA.0 |   IN | 1 | 27 || 28 | 1 | IN   | SCL.0   | 31  | 1   |
 |   5 |  21 | GPIO.21 |   IN | 1 | 29 || 30 |   |      | 0v      |     |     |
 |   6 |  22 | GPIO.22 |   IN | 1 | 31 || 32 | 0 | IN   | GPIO.26 | 26  | 12  |
 |  13 |  23 | GPIO.23 |  OUT | 1 | 33 || 34 |   |      | 0v      |     |     |
 |  19 |  24 | GPIO.24 |   IN | 0 | 35 || 36 | 0 | IN   | GPIO.27 | 27  | 16  |
 |  26 |  25 | GPIO.25 |  OUT | 0 | 37 || 38 | 0 | OUT  | GPIO.28 | 28  | 20  |
 |     |     |      0v |      |   | 39 || 40 | 0 | OUT  | GPIO.29 | 29  | 21  |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
 +-----+-----+---------+------+---+---Pi 3B+-+---+------+---------+-----+-----+


# 参考文献
IPを固定する
https://qiita.com/hujuu/items/f3799946d761006c9852

cron設定ガイド
https://www.express.nec.co.jp/linux/distributions/knowledge/system/crond.html

光に反応する回路－光センサ回路
https://startelc.com/elc/Works/elc_W_CdsTr.html

FETを電源スイッチの代わりに使用する方法メモ
https://memoteki.net/archives/1352

オートロックを自動解除したい[ラズパイ]
https://qiita.com/KTKT2070/items/f806381af0d57183aefa
