# -*- coding: utf-8 -*-
#ab打数 hit安打 bb四球 hbp死球 sf犠牲フライ

import math
import time
import psycopg2

FIVE_PERSENT = 5
ONE_PERSENT = 1

#基本成績クラス 入力するのはこれらの値
class Record:
	def __init__(self, myYear, myAb, myHit, myBb, myHbp, mySf):
		self.year = float(myYear)
		self.ab = float(myAb)
		self.hit = float(myHit)
		self.bb = float(myBb)
		self.hbp = float(myHbp)
		self.sf = float(mySf)
		self.obp = self.calc_obp()

	def calc_obp(self):
		try:
			myObp=(self.hit+self.bb+self.hbp)/(self.ab+self.bb+self.hbp+self.sf)
			return myObp
		except Exception as e:
			return 0

	def show(self):
		print "year:%d, obp:%.3f, ab:%d, hit:%d, bb:%d, hpp:%d, sf:%d" % (self.year, self.obp, self.ab, self.hit, self.bb, self.hbp, self.sf)


#拡張成績クラス
class AdvancedRecord(Record):
	def __init__(self, myYear, myAb, myHit, myBb, myHbp, mySf, myTotalPa, myTotalObp, myZobp, myEvaluation, myGap):
		Record.__init__(self, myYear, myAb, myHit, myBb, myHbp, mySf)
		self.total_pa = float(myTotalPa)
		self.total_obp = float(myTotalObp)
		self.zobp = float(myZobp)
		self.evaluation = myEvaluation
		self.gap = myGap
	#override
	def show(self):
		print "year:%d, total_obp:%.3f obp:%.3f, ab:%3d, zobp:%.3f eva:%s gap:%.3f hit:%d, bb:%d, hpp:%d, sf:%d" % (self.year, self.total_obp, self.obp, self.ab, self.zobp, self.evaluation, self.gap, self.hit, self.bb, self.hbp, self.sf)


#拡張成績クラスと基本成績クラスで成績が入っている箱。
#基本成績を入れると、拡張成績が作られるすぐれもの
#ars=advanced records
class RecordBox:
	def __init__(self, myRecords):
		self.records = myRecords
		self.totalism_ars = self.make_totalism_ars(FIVE_PERSENT)
		self.impermanancism_five_ars = self.make_impermanancism_ars(FIVE_PERSENT)
		self.impermanancism_one_ars = self.make_impermanancism_ars(ONE_PERSENT)

	def make_totalism_ars(self, level):
		ars = []
		zobp = 0
		time_of_the_change = 0 #カウントの何回目が最後の能力変化か記録する変数。あるけど使っていない
		for i,r in enumerate(self.records):
			total_n, total_obp = self.calc_total_obp(i, 0) #通算OPBと打数を計算する。常に通算計算の起点は0
			latest_n=r.ab+r.bb+r.hbp+r.sf #今シーズンのnを算出する(ほぼPAだけど厳密に、AB+BB+HBP+SFしてる)
			zobp = self.calc_zobp(total_n, total_obp, latest_n, r.obp) #現在の今年度成績と通算成績とを比較してzOBPを出す
			evaluation, time_of_the_change = self.evaluate_zobp(zobp, i, time_of_the_change, level) #zOBPに応じて覚醒を記録する
			gap = r.obp - total_obp#現在の今年度成績と通算成績(即ち予測値)との差を出す
			ar = AdvancedRecord(r.year, r.ab, r.hit, r.bb, r.hbp, r.sf, total_n, total_obp, zobp, evaluation, gap) #通算成績と、zOBPを追加したAdvancedRecordを作る
			ars.append(ar) #arsに追加
		return ars
	
	def make_impermanancism_ars(self, level):
		ars = []
		zobp = 0
		time_of_the_change = 0 #カウントの何回目が最後の能力変化か記録する変数
		for i,r in enumerate(self.records):
			total_n, total_obp = self.calc_total_obp(i, time_of_the_change) #覚醒後通算OBPと覚醒後通算打数を計算する
			latest_n=r.ab+r.bb+r.hbp+r.sf #今シーズンのnを算出する(ほぼPAだけど厳密に、AB+BB+HBP+SFしてる)
			zobp = self.calc_zobp(total_n, total_obp, latest_n, r.obp) #現在の今年度成績と覚醒後通算成績とを比較してzOBPを出す
			evaluation, time_of_the_change = self.evaluate_zobp(zobp, i, time_of_the_change, level) #zOBPに応じて覚醒を記録する
			gap = r.obp - total_obp#現在の今年度成績と通算成績(即ち予測値)との差を出す
			ar = AdvancedRecord(r.year, r.ab, r.hit, r.bb, r.hbp, r.sf, total_n, total_obp, zobp, evaluation, gap) #通算成績と、zOBPを追加したAdvancedRecordを作る
			ars.append(ar) #arsに追加
		return ars
	
	def calc_total_obp(self, latest, oldest):
		total_ab = 0
		total_hit = 0
		total_bb = 0
		total_hbp = 0
		total_sf = 0
		for i in range(oldest, latest):
			total_ab += self.records[i].ab
			total_hit += self.records[i].hit
			total_bb += self.records[i].bb
			total_hbp += self.records[i].hbp
			total_sf += self.records[i].sf
		total_obp = self.calc_obp(total_ab, total_hit, total_bb, total_hbp, total_sf)
		return total_ab+total_bb+total_hbp+total_sf, total_obp

	def calc_obp(self, myAb, myHit, myBb, myHbp, mySf):
		try:
			myObp=(myHit+myBb+myHbp)/(myAb+myBb+myHbp+mySf)
			return myObp
		except Exception as e:
			return 0

	def calc_zobp(self, my_total_pa, my_total_obp, my_latest_pa, my_latest_obp):
		try:
			zobp = ((my_latest_obp - my_total_obp) /
			       math.sqrt((my_latest_obp * (1 - my_latest_obp) / my_latest_pa) + (my_total_obp * (1 - my_total_obp) / my_total_pa)))
			return zobp
		except Exception as e:
			return 0

	def evaluate_zobp(self, myZobp, time, my_time_of_the_change, p_value):
		if(p_value==FIVE_PERSENT):
			if myZobp > 1.96: #上側2.5%点
				return "覚醒", time
			elif myZobp > 0.67: #上側25%点
				return "幸運", my_time_of_the_change
			elif myZobp > -0.67: #真ん中、全体の50%
				return "普通", my_time_of_the_change
			elif myZobp > -1.96: #下側25%点
				return "不運", my_time_of_the_change
			else: #下側2.5%点
				return "逆覚醒", time
		elif(p_value==ONE_PERSENT):
			if myZobp > 2.57: #上側0.5%点
				return "覚醒", time
			elif myZobp > 0.67: #上側25%点
				return "幸運", my_time_of_the_change
			elif myZobp > -0.67: #真ん中、全体の50%
				return "普通", my_time_of_the_change
			elif myZobp > -2.57: #下側25%点
				return "不運", my_time_of_the_change
			else: #下側0.5%点
				return "逆覚醒", time
		else:
			if myZobp > 1.96: #上側2.5%点
				return "覚醒", time
			elif myZobp > 0.67: #上側25%点
				return "幸運", my_time_of_the_change
			elif myZobp > -0.67: #真ん中、全体の50%
				return "普通", my_time_of_the_change
			elif myZobp > -1.96: #下側25%点
				return "不運", my_time_of_the_change
			else: #下側2.5%点
				return "逆覚醒", time


#Player
class Player:
	def __init__(self, myRecordBox, myName):
		self.recordbox = myRecordBox
		self.name = myName

	def show_totalism_records(self):
		print "\n--- totalism records ---"
		for r in self.recordbox.totalism_ars:
			r.show()
		print "--- end ---\n"

	def show_impermanancism_five_records(self):
		print "\n--- impermanancism 5 persent records ---"
		for r in self.recordbox.impermanancism_five_ars:
			r.show()
		print "--- end ---\n"

	def show_impermanancism_one_records(self):
		print "\n--- impermanancism 1 persent records ---"
		for r in self.recordbox.impermanancism_one_ars:
			r.show()
		print "--- end ---\n"

	def show_gaps(self):
		print "\n--- gaps ---"
		sum_of_sq_gap = 0
		for r in self.recordbox.impermanancism_five_ars:
			sum_of_sq_gap += r.gap
		print "impermanancism5p:\t%f" % (sum_of_sq_gap)
		sum_of_sq_gap = 0
		for r in self.recordbox.impermanancism_one_ars:
			sum_of_sq_gap += r.gap
		print "impermanancism1p:\t%f" % (sum_of_sq_gap)
		sum_of_sq_gap = 0
		for r in self.recordbox.totalism_ars:
			sum_of_sq_gap += r.gap
		print "totalism:\t%f" % (sum_of_sq_gap)
		print "--- end ---\n"

	def show_sq_gaps(self):
		print "\n--- squared gaps ---"
		sum_of_sq_gap = 0
		for r in self.recordbox.impermanancism_five_ars:
			sum_of_sq_gap += r.gap**2
		print "impermanancism5p:\t%f" % (sum_of_sq_gap)
		sum_of_sq_gap = 0
		for r in self.recordbox.impermanancism_one_ars:
			sum_of_sq_gap += r.gap**2
		print "impermanancism1p:\t%f" % (sum_of_sq_gap)
		sum_of_sq_gap = 0
		for r in self.recordbox.totalism_ars:
			sum_of_sq_gap += r.gap**2
		print "totalism:\t%f" % (sum_of_sq_gap)
		print "--- end ---\n"


def show_sq_gaps(myPlayers):
	sum_of_sq_gap = 0

	print "\n--- squared gaps ---"

	print "impermanancism5p:\t",
	for player in myPlayers:
		for r in player.recordbox.impermanancism_five_ars:
			sum_of_sq_gap += r.gap**2
	print "%f\n" % sum_of_sq_gap
	sum_of_sq_gap = 0

	print "impermanancism1p:\t",
	for player in myPlayers:
		for r in player.recordbox.impermanancism_one_ars:
			sum_of_sq_gap += r.gap**2
	print "%f\n" % sum_of_sq_gap
	sum_of_sq_gap = 0

	print "totalism:\t",
	for player in myPlayers:
		for r in player.recordbox.totalism_ars:
			sum_of_sq_gap += r.gap**2
	print "%f\n" % sum_of_sq_gap
	sum_of_sq_gap = 0


def show_deviation(myPlayers):
	sum_of_sq_gap = 0

	print "\n--- deviation ---"

	print "impermanancism5p:\t",
	for player in myPlayers:
		for r in player.recordbox.impermanancism_five_ars:
			sum_of_sq_gap += r.gap**2
	print "%f\n" % math.sqrt(sum_of_sq_gap/len(myPlayers))
	sum_of_sq_gap = 0

	print "impermanancism1p:\t",
	for player in myPlayers:
		for r in player.recordbox.impermanancism_one_ars:
			sum_of_sq_gap += r.gap**2
	print "%f\n" % math.sqrt(sum_of_sq_gap/len(myPlayers))
	sum_of_sq_gap = 0

	print "totalism:\t",
	for player in myPlayers:
		for r in player.recordbox.totalism_ars:
			sum_of_sq_gap += r.gap**2
	print "%f\n" % math.sqrt(sum_of_sq_gap/len(myPlayers))
	sum_of_sq_gap = 0


##------------------------------------------------------------------------------------------------
print "connecting...\n"
conn = psycopg2.connect(dbname="postgres", host="localhost", port=5432, user="postgres", password="postgres")
print "connected!\n"

#name = "Tomoaki Kanemoto"
#sql = "SELECT * FROM batter_data WHERE name LIKE \'%" + name + "\';"
sql = "SELECT * FROM batter_data;"

cur = conn.cursor()
cur.execute(sql)

all_of_them = cur.fetchall()

cur.close()
conn.close()

print "start making players"
players = [] #選手をぶちこむリスト
records = [] #成績を"一時的に"ぶちこむリスト
first_row_index = None #各選手の成績の最初の行を一時的に保存する
name = None #各選手の名前を一時的に保存する
for i, row in enumerate(all_of_them):
	tmp_name = row[0]#名前を取得する
	if (tmp_name!=name): #名前がさっきまでの名前と違ったら
		players.append(Player(RecordBox(records), name))#いままでのをレコードボックスにいれてレコードボックスをプレイヤーにいれて、プレイやーをぷれいやーずにいれる
		records = [] #recordsをリセット
		name = tmp_name #さっきまでの名前を入れ替える
		first_row_index = i #いまのインデックスを最初のrowにする
	#もしこの行が使える行なら、recordsにいれる。
	if( isinstance(row[1],int) and isinstance(row[8],int) and isinstance(row[10],int) and isinstance(row[17],int) and isinstance(row[25],int) and isinstance(row[27],int) ):
		records.append(Record(row[1],row[8],row[10],row[17],row[25],row[27])) #recordsに加える
	if( i%(len(all_of_them)/50)==0 ):
		print "#",
print "done\n"
time.sleep(1)




if __name__ == '__main__':
	show_sq_gaps(players)
	show_deviation(players)
	#player_id = 10
	#players[player_id].show_impermanancism_five_records()
	#players[player_id].show_impermanancism_one_records()
	#players[player_id].show_totalism_records()
	#players[player_id].show_gaps()
	#players[player_id].show_sq_gaps()
	#print players[player_id].name