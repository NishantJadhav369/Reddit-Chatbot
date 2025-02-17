import json
import sqlite3
from datetime import datetime
import pandas

timeframe = '2015-01'
sql_transaction = []

#connection = sqlite3.connect('{}.db'.format("tp3"))
c = connection.cursor()

def find_parent(pid):
	try:
		sql = """SELECT comment FROM parent_reply WHERE comment_id ='{}' LIMIT 1""".format(pid)
		c.execute(sql)
		result = c.fetchone()
		#print("hi")
		#print(result)
		if result!= None:
			return result[0]
		else: return False
	except Exception as e:
		#print("his")
		print("find parent",e)
		return False

def transaction_bldr(sql):
	global sql_transaction
	sql_transaction.append(sql)
	if len(sql_transaction)>1000:
		c.execute('BEGIN TRANSACTION')
		for s in sql_transaction:
			try:
				c.execute(s)
			except:
				pass
		connection.commit()
		sql_transaction =[]



def sql_insert_replace_comment(commentid,parentid,parent,comment,subreddit,time1,score):
	try:
		#print("Replace comment")
		sql = """UPDATE parent_reply SET parent_id = ?,commentid =?,parent=?,comment=?,subreddit=?,unix=?,score=? WHERE parent_id = ?;""".format(parentid,commentid,parent,comment,subreddit,time1,score)
		transaction_bldr(sql)
	except Exception as e:
		print('s-UPDATE insertion',str(e))

def sql_insert_has_parent(commentid,parentid,parent,comment,subreddit,time1,score):
	try:
		#print(" has parent activated")
		sql = """INSERT INTO parent_reply (parent_id ,comment_id ,parent ,comment ,subreddit ,unix ,score) VALUES ("{}","{}","{}","{}","{}",{},{});""".format(parentid,commentid,parent,comment,subreddit,time1,score)
		transaction_bldr(sql)
	except Exception as e:
		print('s-PARENT insertion',str(e))

def sql_insert_no_parent(commentid,parentid,comment,subreddit,time1,score):
	try:
		#print("Insert no_parent ")
		sql = """INSERT INTO parent_reply (parent_id ,comment_id ,comment ,subreddit ,unix ,score) VALUES ("{}","{}","{}","{}",{},{});""".format(parentid,commentid,comment,subreddit,time1,score)
		transaction_bldr(sql)
	except Exception as e:
		print('s-NO_PARENT insertion',str(e))


def find_existing_score(pid):
	try:
		sql = "SELECT score FROM parent_reply WHERE parent_id = '{}' LIMIT 1".format(pid)
		c.execute(sql)
		result = c.fetchone()
		if result != None:
			#print("FOUND")
			return result[0]
		else: return False
	except Exception as e:
		print("existing_score_exception ",str(e))
		return False

def acceptable(data):
	if len(data.split(' '))> 50 or len(data)<1:
		return False
	elif len(data) > 1000:
		return False
	elif data == '[deleted]' or data =='[removed]':
		return False
	else:
		return True


def create_table():
	c.execute(""" CREATE TABLE IF NOT EXISTS parent_reply(parent_id TEXT PRIMARY KEY,
		comment_id TEXT UNIQUE,parent TEXT,comment TEXT,subreddit TEXT,unix INT,score INT)""")

def format_data(data):
	data = data.replace("\n"," newlinechar ").replace("\r"," newlinechar ").replace('"',"'")
	return data

if __name__ == "__main__":
	create_table()
	row_counter =0
	paired_rows = 0
	c1=0

	with open("F:/Dataset/RC_{}/RC_{}".format(timeframe,timeframe),buffering=1000) as f: #bufferError
		for row in f:
			c1 +=1
			#print(row)

			if(c1==2000000):
				break
			
			row_counter +=1
			#print(row_counter)
			row = json.loads(row)
			parent_id = row['parent_id']
			body = format_data(row['body'])
			created_utc = row['created_utc']
			score = row['score']
			subreddit = row['subreddit']
			parent_data = find_parent(parent_id) 
			#print(parent_data)
			comment_id = row['name']      
			
			if score >=2:
				if acceptable(body):
					#print("accepted\n")
					existing_comment_score = find_existing_score(parent_id)
					#print(existing_comment_score)
					
					if existing_comment_score:
						#print(parent_data)
						if score > existing_comment_score:
							sql_insert_replace_comment(comment_id,parent_id,parent_data,body,subreddit,created_utc,score)
					else:
						if parent_data:
							#print("parent_data")
							sql_insert_has_parent(comment_id,parent_id,parent_data,body,subreddit,created_utc,score)
							paired_rows +=1
							#print(paired_rows)
						else:
							#print("no _parent")
							sql_insert_no_parent(comment_id,parent_id,body,subreddit,created_utc,score)
			if row_counter % 100000 == 0:

				print("Total rows read: {},Paired rows {},Time :{}".format(row_counter,paired_rows,str(datetime.now())))
			
	