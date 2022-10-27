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
どのデータを取得したいかは、日付の指定までならできる。時間の指定まではできない。また、`logicIndexData`か`summaryData`かは`main.py`にある`keyword`変数で変更できる。
今のところは、`summaryData`しか使う予定はない。

## Google Driveからデータを削除
```bash
python main.py -w yyyymmmdd -D
```
どのデータを削除するかは、日付の指定までならできる。

## グラフの作成
```bash
python main.py -w yyyymmdd -c
#実行するとどの時間帯のデータをグラフにするか入力を求められる
```
どのデータでグラフを作るかは、日付の指定と時間の指定もできる。`keyword`で作るグラフのデータも変更できる。

## 疲労度の記録をするスクリプト
`fatigue.py`では、疲労度を記録することができる。また、`Jins meme`で実験の際にDT作業開始と同時にこのスクリプトを実行すれば「瞬目の間隔時間平均」と「疲労度」を「VDT作業開始時からの経過時間」で結びつけることができる。
詳しい仕様は[こちらのPR](https://github.com/haruya3/graduate-project/pull/5)を参考に。