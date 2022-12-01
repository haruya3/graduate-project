# graduate-project
[Jins API](https://jins-meme.github.io/sdkdoc2/)を利用して、瞬きの間隔の時間を取得する。瞬きと疲労度(目による)との関係性を用いて、疲労がたまる(VDT症候群などになる)前に適切な休憩タイミングの提示を行う。
そのために、このリポジトリでは上記のようなデータを取得しグラフにするまでの自動化を行っていく。

# 使い方
```bash
#オプションを確認
python main.py -h
```
## Google Driveからデータを取得
```bash
python main.py -w yyyymmdd -d
```
どのデータを取得したいかは、日付の指定までならできる。時間の指定まではできない。また、`logicIndexData`か`summaryData`かは`main.py`にある`jins_meme_data_name`変数で変更できる。
今のところは、`summaryData`しか使う予定はない。

## Google Driveからデータを削除
```bash
python main.py -w yyyymmmdd -D
```
どのデータを削除するかは、日付の指定までならできる。

## グラフの作成
```bash
python main.py -w yyyymmdd -cG
#実行するとどの時間帯のデータをグラフにするか入力を求められる
```
どのデータでグラフを作るかは、日付の指定と時間の指定もできる。例えば、`15`とすれば15時での実験の結果のグラフを作成する。`15-16`とすれば、15時から16時での実験の結果のグラフを作成する。注意点は、**この場合実験開始時刻が15時なので`16`と指定はできない**(プログラムは実行されない)。`keyword`で作るグラフのデータも変更できる。

### 疲労度のファイルパス
疲労度のファイルパスはJins memeがGoogle Driveに作成したCSVファイルの中にある`date`キーの値(時間)を使っている。また、`pass_time`という経過時間は`datetime.datetime.now`と`start_time`([`get_start_time`というコードを参考](https://github.com/haruya3/graduate-project/blob/master/my_google/my_drive/helper.py#L37))を元にしている。**この`date`キーの値と`pass_time`の値にはずれが生じることがある**。`date`キーの時間が`datetime.datetime.now`と1分ほどずれる時があり、それによって5分毎に疲労度のファイルパスを読み取る処理で疲労度のファイルパスもずれてしまい読みこめない。
#### そこで読み込めなかった疲労度のファイルパスを表示することで、そのファイルパスを1分ほどずらせば読み込めるようにできるよう改良した。
ファイルパスを1分ずらせば`date`キーのずれを解消して`pass_time`で5分毎のタイミングに合わせることができる。

## 表の作成
```bash
python main.py -w yyyymmdd -cT
```
疲労度ごとの瞬目の間隔時間平均の振り幅の表作成。また、疲労度ごとの瞬目の間隔時間平均の平均値の表も作成できる。形式はtablefmtで指定していて今は**html形式**となっている。よって、マークダウン方式の記事などにコピペで表を表示できる。

## 疲労度の記録をするスクリプト
`fatigue.py`では、疲労度を記録することができる。また、`Jins meme`で実験の際にDT作業開始と同時にこのスクリプトを実行すれば「瞬目の間隔時間平均」と「疲労度」を「VDT作業開始時からの経過時間」で結びつけることができる。
詳しい仕様は[こちらのPR](https://github.com/haruya3/graduate-project/pull/5)を参考に。
