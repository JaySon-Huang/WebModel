# -*- coding: utf-8 -*-
import sqlite3
from WebModel.items import PageItem

VERBOSE = 1

CTABLE_DOMAIN = '''
CREATE TABLE IF NOT EXISTS Domains(
 did INTEGER PRIMARY KEY AUTOINCREMENT,
 indegree INTEGER,
 outdegree INTEGER,
 domain VARCHAR(64)
)'''

CTABLE_WEBSITE = '''
CREATE TABLE IF NOT EXISTS Websites(
 wid INTEGER PRIMARY KEY AUTOINCREMENT,
 did INTEGER,
 url VARCHAR(256) NOT NULL,
 title VARCHAR(100),
 visited bit,
 FOREIGN KEY (did) REFERENCES Domains(did)
)'''

CTABLE_RULESETS = '''
CREATE TABLE IF NOT EXISTS Rulesets(
 rid INTEGER PRIMARY KEY AUTOINCREMENT,
 did INTEGER,
 rules VARCHAR(512),
 FOREIGN KEY (did) REFERENCES Domains(did)
)'''

# CTABLE_W2R = '''
# CREATE TABLE IF NOT EXISTS WtoR(
#  wid INTEGER,
#  rid INTEGER,
#  PRIMARY KEY (wid,rid),
#  FOREIGN KEY (wid) REFERENCES Websites(wid),
#  FOREIGN KEY (rid) REFERENCES Robots(rid)
# )'''

class DatabaseHelper(object):
	def __init__(self):
		'''创建表'''
		self.conn = sqlite3.connect("./items.db")
		if VERBOSE:
			print 'Database connection OPEN.'
		# Domain 表
		self.conn.execute(CTABLE_DOMAIN)
		# Website 表
		self.conn.execute(CTABLE_WEBSITE)
		# Rule 表 
		self.conn.execute(CTABLE_RULESETS)
		self.conn.commit()
		if VERBOSE:
			cur = self.conn.cursor()
			print 'Tables:',cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()

	def close(self):
		'''关闭与数据库的连接'''
		if VERBOSE:
			print 'Database connection CLOSE.'
		self.conn.close()

	def insertDomain(self, domain):
		'''增加一个域名'''
		cur = self.conn.cursor()
		cur.execute("INSERT INTO Domains VALUES (NULL,0,0,?)", (domain,))
		# 写入到文件中
		self.conn.commit()

	def insertRuleset(self, ruleset, domain):
		'''增加一个robots.txt规则集'''
		cur = self.conn.cursor()
		cur.execute("SELECT did FROM Domains WHERE domain=?", (domain,))
		did = cur.fetchone()[0]
		cur.execute("INitemSERT INTO Rulesets VALUES (NULL,?,?)",(did,ruleset))
		# 写入到文件
		self.conn.commit()
	
	def insertWebsite(self, url, domain):
		'''增加一个网页,标记为未访问'''
		cur = self.conn.cursor()
		cur.execute("SELECT did FROM Domains WHERE domain=?", (domain,))
		did = cur.fetchone()[0]
		cur.execute("INSERT INTO Websites VALUES (NULL,?,?,NULL,0)", (did, url,))
		# 写入到文件
		self.conn.commit()
		pass

	def updateInfo(self, item):
		'''爬虫爬完之后对数据库内容进行更新'''
		cur = self.conn.cursor()
		cur.execute("SELECT wid,did FROM Websites WHERE url=?", (item.url,))
		wid, did = cur.fetchone()
		# website记录更新
		cur.execute("UPDATE Websites SET title=?,visited=1 WHERE wid=?", (item.title, wid,))
		# 对应的domain记录中入度出度也需要更新
		cur.execute("UPDATE Domains SET outdegree=outdegree+? WHERE did=?", (len(item.links), did,))
		# 写入到文件
		self.conn.commit()
		pass

	def addDomainIndegree(self, url, numToAdd):
		'''当读到其他网页对当前域名有链接时, 更新对这个域名的入度计数'''
		cur = self.conn.cursor()
		cur.execute("SELECT did FROM Websites WHERE url=?", (item.url,))
		did = cur.fetchone()[0]
		cur.execute("UPDATE Domains SET outdegree=outdegree+? WHERE did=?", (numToAdd, did,))
		# 写入到文件
		self.conn.commit()

	def robotsrulesetOfDomain(self, domain):
		'''检查domain是否在数据库中,
			否 --> (False, None)
			是 --> (True, 数据库中存储的robots.txt内容)
		'''
		exist = False
		cur = self.conn.cursor()
		# 是否存在
		cur.execute("SELECT 1 FROM Domains WHERE domain=?", (domain,))
		if cur.fetchone() :
			exist = True
		# 存在的话,结果是什么
		cur.execute("SELECT rules FROM Domains,Rulesets "
			"WHERE domain=? AND Domains.did=Rulesets.did"
			,(domain,) )
		print cur.fetchone()

dbcli = DatabaseHelper()

if __name__ == '__main__':
	dbcli = DatabaseHelper()
	# dbcli.insert_domain('jaysonhwang.com')
	# dbcli.insert_ruleset('test','jaysonhwang.com')
	dbcli.robotsrulesetOfDomain('jaysonhwang.com')
	dbcli.close()
