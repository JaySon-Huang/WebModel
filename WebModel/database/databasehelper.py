# -*- coding: utf-8 -*-
import sqlite3


VERBOSE = 0

CTABLE_DOMAIN = '''
CREATE TABLE IF NOT EXISTS Domains(
 did INTEGER PRIMARY KEY AUTOINCREMENT,
 domain VARCHAR(64) UNIQUE,
 indegree INTEGER,
 outdegree INTEGER
)'''

CTABLE_WEBSITE = '''
CREATE TABLE IF NOT EXISTS Websites(
 wid INTEGER PRIMARY KEY AUTOINCREMENT,
 did INTEGER,
 url VARCHAR(256) NOT NULL UNIQUE,
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

	def insertDomain(self, domain, indegree=0, outdegree=0):
		'''增加一个域名'''
		cur = self.conn.cursor()
		cur.execute("INSERT INTO Domains VALUES (NULL,?,?,?)", (domain, indegree, outdegree))
		# 写入到文件中
		self.conn.commit()

	def insertRuleset(self, ruleset, domain):
		'''增加一个robots.txt规则集'''
		cur = self.conn.cursor()
		cur.execute("SELECT did FROM Domains WHERE domain=?", (domain,))
		did = cur.fetchone()[0]
		cur.execute("INSERT INTO Rulesets VALUES (NULL,?,?)",(did, ruleset))
		# 写入到文件
		self.conn.commit()
	
	def insertWebsite(self, url, domain):
		'''增加一个网页,标记为未访问,并对相应的domain增加其入度'''
		cur = self.conn.cursor()
		cur.execute("SELECT 1 FROM Domains WHERE domain=?", (domain,))
		result = cur.fetchone()
		if not result:
			# 未有对应domain记录, 先创建domain, 把入度设为1
			if VERBOSE:
				print 'Spot Domain:',domain
			self.insertDomain(domain, indegree=1)
			cur.execute("SELECT did FROM Domains WHERE domain=?", (domain,))
			did = cur.fetchone()[0]
		else:
			did = result[0]
			# 对应的domain记录已经存在, 对其入度+1
			cur.execute("UPDATE Domains SET outdegree=outdegree+1 WHERE domain=?", (domain,))

		cur.execute("INSERT INTO Websites VALUES (NULL,?,?,NULL,0)", (did, url,))
		# 写入到文件
		self.conn.commit()

	def updateInfo(self, item, newlinks, oldlinks):
		'''爬虫爬完之后对数据库内容进行更新'''
		cur = self.conn.cursor()
		cur.execute("SELECT wid,did FROM Websites WHERE url=?", (item['url'],))
		wid, did = cur.fetchone()
		# website记录更新
		cur.execute("UPDATE Websites SET title=?,visited=1 WHERE wid=?", (item['title'], wid,))
		# 对应的domain记录中出度也需要更新
		cur.execute("UPDATE Domains SET outdegree=outdegree+? WHERE did=?", (len(item['links']), did,))

		# 对该网页中所有链接涉及的记录进行更新
		# 外部判断未出现过的链接
		for link,domain in newlinks:
			self.insertWebsite(link, domain)

		# 外部判断出现过的链接
		for link,domain in oldlinks:
			# 对对应的domain记录入度增加
			cur.execute("UPDATE Domains SET outdegree=outdegree+1 WHERE domain=?", (domain,))
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
		ruleset = cur.fetchone()
		return (exist, ruleset)

	def rollback(self):
		self.conn.rollback()

	def showAll(self):
		self.conn.commit()
		cur = self.conn.cursor()
		cur.execute("SELECT * FROM Domains")
		print cur.fetchall()
		cur.execute("SELECT * FROM Websites")
		print cur.fetchall()

_dbcli = None

def getCliInstance():
	global _dbcli
	if not _dbcli:
		_dbcli = DatabaseHelper()
	return _dbcli

def test():
	dbcli = getCliInstance()
	# dbcli.insertDomain('jaysonhwang.com')
	# dbcli.insertRuleset('test','jaysonhwang.com')
	print dbcli.robotsrulesetOfDomain('www.zol.com')
	print dbcli.robotsrulesetOfDomain('jayson.com')
	dbcli.showAll()
	dbcli.close()

if __name__ == '__main__':
	test()
