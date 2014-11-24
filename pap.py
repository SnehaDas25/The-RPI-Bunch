#!flask/bin/python
import os, sys, random
import psycopg2
import urlparse
from flask import Flask, jsonify, abort, request, make_response, url_for, render_template


app = Flask(__name__)

def connect_db():
	conn = None
	urlparse.uses_netloc.append("postgres")
	#url = urlparse.urlparse(os.environ["DATABASE_URL"])
	#print url
	#conn = psycopg2.connect(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
	conn = psycopg2.connect(database='sdas', user=None, password=None, host=None, port=None)
	return conn


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)
 
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)




@app.route('/mas/api/v1.0/tasks/get', methods=['GET'])
def get_table():
	conn = connect_db()
	cur = conn.cursor()

	table = request.args['table']
	sql = "SELECT * FROM " + table + ";"
	cur.execute(sql)
	result = cur.fetchall()
	
	if conn:
		conn.close()
		
	return jsonify({table: result})

@app.route('/mas/api/v1.0/tasks/push', methods=['GET'])
def push():
	gcm = GCM(API_KEY)
	# for key, value in request.args.iteritems():
	# 	print key, value

	# data = {'param1': 'value1', 'param2': 'value2', 'dry_run':'true'}
	# print data
	# print request.args.to_dict()
	data = request.args.to_dict()
	reg_id = REG_ID
	gcm.plaintext_request(registration_id=reg_id, data=data)
	return jsonify({"nothing":"nothing"})

@app.route('/mas/api/v1.0/tasks/getlocations', methods=['GET'])
def get_locations():
	conn = connect_db()
	cur = conn.cursor()
	sql = "SELECT * FROM locations;"
	cur.execute(sql)
	result = cur.fetchall()
	print result
	
	locations = []
	for r in result:
		fields = {}
		fields['loc_id'] = r[0]
		fields['loc_name'] = r[1]
		fields['lat'] = r[2]
		fields['long'] = r[3]
		locations.append(fields)

	if conn:
		conn.close()
	return locations	
	#return jsonify({'locations': locations})

#@app.route('/mas/api/v1.0/tasks/getwalkers', methods=['GET'])
def get_walkers():
	conn = connect_db()
	cur = conn.cursor()
	sql = """SELECT u.gt_id, u.first_name, u.last_name, w.start_time, w.grp_id, g.name, l.name 
				FROM ((walkers w INNER JOIN locations l ON w.dest_id=l.id) INNER JOIN users u on u.gt_id = w.gt_id) 
				LEFT OUTER JOIN groups g on g.id=w.grp_id;"""
	cur.execute(sql)
	result = cur.fetchall()
	print result
	
	walkers = []
	for r in result:
		fields = {}
		fields['gt_id'] = r[0]
		fields['first_name'] = r[1]
		fields['last_name'] = r[2]
		fields['start_time'] = r[3]
		fields['grp_id'] = r[4]
		fields['grp_name'] = r[5]
		fields['dest_name'] = r[6]
		walkers.append(fields)

	if conn:
		conn.close()
		
	return walkers
	#return jsonify({'walkers': walkers})


@app.route('/mas/api/v1.0/tasks/getuser', methods=['GET'])
def get_user():
	conn = connect_db()
	cur = conn.cursor()

	sql = "SELECT * FROM users WHERE gt_id = \'" + request.args['gt_id'] + "\';"
	cur.execute(sql)
	result = cur.fetchone()
	if result == None:
	   	abort(404)

	user = {}
	user['gt_id'] = result[0]
	user['first_name'] = result[1]
	user['last_name'] = result[2]
	user['def_dest'] = result[3]
	print user
	
	if conn:
		conn.close()
	return user	
	#return jsonify({'user': user})


@app.route('/mas/api/v1.0/tasks/addgroup', methods=['POST'])
def add_group():
	if not request.form or not 'grp_id' in request.form:
		abort(400)

	grp_id = request.form['grp_id']
	name = request.form['name']
	dest_id = request.form['dest_id']

	if name=="":
		name += "Group" + str(random.randint(100,999)) + str(grp_id)

	conn = connect_db()
	cur = conn.cursor()

	sql = "INSERT INTO groups VALUES (" + grp_id + ", '" + name + "', " + dest_id + ");" 
	cur.execute(sql)
	conn.commit()
	
	if conn:
		conn.close()
		
	return jsonify({'success': 'true'}), 201

@app.route('/mas/api/v1.0/tasks/removegroup', methods=['POST'])
def remove_group():
	if not request.form or not 'grp_id' in request.form:
		abort(400)

	conn = connect_db()
	cur = conn.cursor()

	sql = "DELETE FROM groups where id=" + request.form['grp_id'] + ";" 
	cur.execute(sql)
	conn.commit()
	
	if conn:
		conn.close()
		
	return jsonify({'success': 'true'}), 201

@app.route('/mas/api/v1.0/tasks/addwalker', methods=['POST'])
def add_walker():
	if not request.form or not 'gt_id' in request.form:
		abort(400)

	gt_id = request.form['gt_id']
	src_id = request.form['src_id']
	dest_id = request.form['dest_id']
	start_time = request.form['start_time']

	conn = connect_db()
	cur = conn.cursor()

	# If user entry exists, then update it, else create a new entry
	sql = "SELECT * FROM walkers WHERE gt_id = \'" + gt_id + "\';"
	cur.execute(sql)
	if cur.fetchone() == None:
		sql = "INSERT INTO walkers VALUES ('" + gt_id + "', " + src_id + ", " + dest_id + ", '" + start_time + "', null);" 
	else:
		sql = "UPDATE walkers set src_id=" + src_id + ", dest_id=" + dest_id + ", start_time='" + start_time + "' WHERE gt_id='" + gt_id + "';"
	cur.execute(sql)
	conn.commit()
	
	if conn:
		conn.close()
		
	return jsonify({'success': 'true'}), 201

@app.route('/mas/api/v1.0/tasks/removewalker', methods=['POST'])
def remove_walker():
	if not request.form or not 'gt_id' in request.form:
		abort(400)

	conn = connect_db()
	cur = conn.cursor()

	sql = "DELETE FROM walkers where gt_id='" + request.form['gt_id'] + "';" 
	cur.execute(sql)
	conn.commit()
	
	if conn:
		conn.close()
		
	return jsonify({'success': 'true'}), 201

@app.route('/mas/api/v1.0/tasks/adduser', methods=['POST'])
def add_user():
	if not request.form or not 'gt_id' in request.form:
		abort(400)

	gt_id = request.form['gt_id']
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	def_dest = request.form['def_dest']
	email = request.form['email']

	conn = connect_db()
	cur = conn.cursor()

	sql = "INSERT INTO users VALUES ('" + gt_id + "', '" + first_name + "', '" + last_name + "', " + def_dest + ", '" + email +"');" 
	
	cur.execute(sql)
	conn.commit()
	
	if conn:
		conn.close()
		
	return jsonify({'success': 'true'}), 201

@app.route('/mas/api/v1.0/tasks/removeuser', methods=['POST'])
def remove_user():
	if not request.form or not 'gt_id' in request.form:
		abort(400)

	conn = connect_db()
	cur = conn.cursor()

	sql = "DELETE FROM users where gt_id='" + request.form['gt_id'] + "';" 
	cur.execute(sql)
	conn.commit()
	
	if conn:
		conn.close()
		
	return jsonify({'success': 'true'}), 201

@app.route('/mas/api/v1.0/tasks/addlocation', methods=['POST'])
def add_location():
	if not request.form or not 'loc_id' in request.form:
		abort(400)

	loc_id = request.form['loc_id']
	name = request.form['name']
	lat= request.form['lat']
	longi = request.form['long']
#
	conn = connect_db()
	cur = conn.cursor()

	sql = "INSERT INTO locations VALUES (" + loc_id + ", '" + name + "', " + lat + ", " + longi +");" 
	
	cur.execute(sql)
	conn.commit()
	
	if conn:
		conn.close()
		
	return jsonify({'success': 'true'}), 201

@app.route('/mas/api/v1.0/tasks/removelocation', methods=['POST'])
def remove_location():
	if not request.form or not 'loc_id' in request.form:
		abort(400)

	conn = connect_db()
	cur = conn.cursor()

	sql = "DELETE FROM locations where id=" + request.form['loc_id'] + ";" 
	cur.execute(sql)
	conn.commit()
	
	if conn:
		conn.close()
		
	return jsonify({'success': 'true'}), 201

@app.route('/mas/api/v1.0/tasks/joingroup', methods=['POST'])
def join_group():
	if not request.form or not 'gt_id' in request.form:
		abort(400)

	conn = connect_db()
	cur = conn.cursor()
	sql = "UPDATE walkers set grp_id=" + request.form['grp_id'] + " WHERE gt_id='" + request.form['gt_id'] + "';"
	cur.execute(sql)
	conn.commit()
	
	if conn:
		conn.close()
		
	return jsonify({'success': 'true'}), 201

@app.route('/mas/api/v1.0/tasks/leavegroup', methods=['POST'])
def leave_group():
	if not request.form or not 'gt_id' in request.form:
		abort(400)

	conn = connect_db()
	cur = conn.cursor()
	sql = "UPDATE walkers set grp_id = null WHERE gt_id='" + request.form['gt_id'] + "';"
	cur.execute(sql)
	conn.commit()
	
	if conn:
		conn.close()
		
	return jsonify({'success': 'true'}), 201


@app.route('/mas/api/v1.0/tasks/sql=<sql>', methods=['GET'])
def run_sql(sql):
	conn = connect_db()
	cur = conn.cursor()
	cur.execute(sql)
	result = cur.fetchall()
	if len(result) == 0:
	   	abort(404)
	print result

	if conn:
		conn.close()

	return jsonify({'result': result})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/login')
def login():
	 users = get_walkers()
    	 return render_template('login.html', users=users)
    	

    	
@app.route("/profile", methods=["GET", "POST"])
def welcome():
	 users = get_walkers()
	 userName = request.form['username']
	 passWord= request.form['password']
	 current = userName+passWord
	 combos = []
	 for user in users:
	 	combo = user['first_name']+user['gt_id']	
		combos.append(combo)
	 if current in combos:
   	 	return render_template("welcome.html",users=users)
	 else:
		return render_template("loginFail.html")

@app.route("/submit", methods=["GET", "POST"])
def sub():
	users = get_walkers()
	group = int(request.args['grp_id'])
	groupusers =[]
	for user in users:
		if user['grp_id'] == group:
			groupusers.append(user)
	print groupusers
	return render_template("submit.html",groupusers=groupusers,group=group)

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/aboutGroup", methods=["GET", "POST"])
def group():
	users = get_walkers()
	group = int(request.args['grp_id'])
	groupusers = []
	for user in users:
		if user['grp_id'] == group:
			groupusers.append(user)	
	return render_template("group.html",groupusers=groupusers,users=users,group=group)



@app.route("/home")
def home():
	users = get_walkers()
	return render_template("welcome.html",users=users)



@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    return redirect(url_for('login'))
	

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
	app.run(debug=True)


