from flask import Flask, request, jsonify,render_template, send_file
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import logger
import queries
import os

app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DOWNLOAD_FOLDER = 'download_files'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

@app.route('/', methods=['GET'])
def home():
    logger.logit("Rendered home page")
    return 'Powered by <a href="https://codingclub.pichavaram.in" target=_blank>Coding Club</a>'

@app.route('/users', methods = ['GET'])
def users():
    # localhost:5000/users
    query = f'SELECT * from users ;'
    result = queries.runQuery(query,data=None,queryType="non-DQL")
    if len(result) != 0:
        response = {'headers':['User ID','Name',"Group","Check Point 1 TimeStamp","Finish TimeStamp","Rank"],'rows':result}
    else:
        response = {'headers':["No Data"],'rows':[]}
    logger.logit("Rendered `users`")
    return response

@app.route('/config', methods = ['GET'])
def config():
    # localhost:5000/config
    query = f'SELECT * from config ;'
    result = queries.runQuery(query,data=None,queryType="non-DQL")
    if len(result) != 0:
        response = {'headers':["Last Rank","Start 1","Start 2","Start 3","Start 4"],'rows':[result[0][0],result[0][1],result[0][2],result[0][3],result[0][4]]}
    else:
        response = {'headers':["No Data"],'rows':[]}
    logger.logit("Rendered `config`")
    return response



@app.route('/insert_user', methods = ['GET'])
def insertUser():
    user_id = str(request.args.get('user_id'))
    name = str(request.args.get('name'))
    try:
        result = queries.runQuery("INSERT INTO users (uid,name) VALUES (%s,%s)",(user_id,name),"DML")
        response = {'headers':["Success"],'rows':result}
    except Exception as e:
        response = {'headers':["Error"],'rows':[e]}
        logger.logit(f"Error while inserting user: {e}")
    finally:
        return jsonify(response)


@app.route('/getrunners',methods=['GET'])
def get_runners():
    # localhost:2400/getrunners?group_id=A
    group_id = str(request.args.get('group_id'))
    try:
        result = queries.runQuery(f"SELECT * FROM users WHERE group_id='{group_id}'",None,"non-DML")
        response = {'headers':["Success"],'rows':result}
        logger.logit(f"Rendered `get_runners` for group {group_id}")
    except Exception as e:
        response = {'headers':["Error"],'rows':[e]}
        logger.logit(f"Error while inserting user: {e}")
    finally:
        return jsonify(response)


@app.route('/getrunnerinfo',methods=['GET'])
def get_runner_info():
    # localhost:2400/getrunnerinfo?user_id=21f1002369
    user_id = str(request.args.get('user_id'))
    try:
        result = queries.runQuery(f"SELECT * FROM users WHERE uid='{user_id}'",None,"non-DML")
        if len(result)==0:
            response = {'headers':["Error"],'rows':["No Data for this user"]}
        else:
            inserter = []
            inserter.append(result[0][0])
            inserter.append(result[0][1])
            inserter.append(result[0][2])
            if result[0][3]==None:
                inserter.append("Not yet arrived ")
            else:
                inserter.append(result[0][3])
            if result[0][4]==None:
                inserter.append("Not yet arrived")
            else:
                inserter.append(result[0][4])
            if result[0][5]==None:
                inserter.append("Not assigned yet")
            else:
                inserter.append(result[0][5])
            response = {'headers':['User ID','Name',"Group","Check Point 1 TimeStamp","Finish TimeStamp","Rank"],'rows':inserter}
        logger.logit(f"Rendered `get_runner_info` for user {user_id}")
    except Exception as e:
        response = {'headers':["Error"],'rows':[e]}
        logger.logit(f"Error while inserting user: {e}")
    finally:
        return response

@app.route('/admin',methods=['GET'])
def admin():
    # localhost:2400/admin
    return render_template('admin.html')


@app.route('/updatestart',methods=['GET'])
def update_start():
    # localhost:2400/updatestart?seeding_id=1
    seeding_id = int(request.args.get('seeding_id'))
    try:
        result = queries.runQuery(f"SELECT * FROM config",None,"non-DML")
        logger.logit(result) # [(0, None, None, None, None)]
        if result[0][seeding_id]==None:
            curr_time = logger.get_time()
            queries.runQuery(f"UPDATE config SET start_{seeding_id}='{curr_time}'",None,"DML")
            result = queries.runQuery(f"UPDATE users SET start='{curr_time}' WHERE seeding_id='{seeding_id}'",None,"DML")
            response = {'headers':["Success"],'rows':f"Updated Start time for {seeding_id} to {curr_time}"}
            logger.logit(f"Updated Start time for {seeding_id} to {curr_time}")
        else:
            response = {'headers':["Error"],'rows':f"Start time already set for {seeding_id}"}
            logger.logit(f"Time for `{seeding_id}` Seeding already set")
    except Exception as e:
        error = "No Runner data" if len(result)==0 else e
        response = {'headers':["Error"],'rows':[error]}
        logger.logit(f"Error while inserting user: {error}")
    finally:
        return jsonify(response)

@app.route('/updatecheckpoint',methods=['GET'])
def update_checkpoint():
    # localhost:2400/updatecheckpoint?user_id=21f1002369
    user_id = str(request.args.get('user_id'))
    try:
        queries.runQuery(f"UPDATE users SET cp1='{logger.get_time()}' WHERE uid='{user_id}'",None,"DML")
        result = queries.runQuery(f"UPDATE users SET cp1='{logger.get_time()}' WHERE uid='{user_id}'",None,"DML")
        response = {'headers':["Success"],'rows':result}
        logger.logit(f"Updated checkpoint for user `{user_id}`")
    except Exception as e:
        response = {'headers':["Error"],'rows':[e]}
        logger.logit(f"Error while inserting user: {e}")
    finally:
        return jsonify(response)

@app.route('/updatefinish',methods=['GET'])
def update_finish():
    # localhost:2400/updatefinish?user_id=21f1002369
    user_id = str(request.args.get('user_id'))
    try:
        # localhost:2400/updatefinish?user_id=21f1002369
        rank = queries.runQuery(f"SELECT * FROM config",None,"non-DML")
        rank = rank[0][0]
        queries.runQuery(f"UPDATE config SET last_rank={rank+1}",None,"DML")
        queries.runQuery(f"UPDATE users SET finish='{logger.get_time()}',rank={rank+1} WHERE uid='{user_id}'",None,"DML")
        response = {'headers':["Success"],'rows':rank}
        logger.logit(f"Updated finish for user `{user_id}` with rank {rank+1}")
    except Exception as e:
        response = {'headers':["Error"],'rows':[e]}
        logger.logit(f"Error while inserting user: {e}")
    finally:
        return jsonify(response)

@app.route('/upload')
def page_upload():
    # localhost:2400/upload
    return render_template('uploader.html')


@app.route('/uploader', methods = ['GET','POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        # Path for file 
        path_of_csv = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # Saving File
        file.save(path_of_csv)
        logger.logit("CSV Uploaded")
        import csv
        with open(path_of_csv, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            val = []
            for row in csvreader:
                val.append((row[0],row[1],int(row[2]),row[3]))
        try:
            success = queries.runQuery("INSERT INTO users (uid,name,seeding_id,group_id) VALUES (%s,%s,%s,%s)",val,"many")
            response = {'headers':["Upload Succesfull"],'rows written':success}
            logger.logit(f"Updated Database with `{success}` rows")
        except Exception as e:
            response = {'headers':["Error while uploading to database"],'rows':[e]}
            logger.logit(f"Error while uploading to database: {e}")
        return response

@app.route('/download')
def downloadCSV():
    # localhost:2400/download
    logger.logit(f"CSV file downloaded")
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], 'Runners_backup.csv'))

@app.route('/delete', methods = ['GET'])
def deleteUserData():
    # localhost:2400/delete
    try:
        if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], 'Runners.csv')):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], 'Runners.csv'))
        queries.runQuery("DELETE FROM users;",None,"DML")
        queries.runQuery("DELETE FROM config;",None,"DML")
        queries.runQuery(f"INSERT INTO config (last_rank,start_1,start_2,start_3,start_4) VALUES (%s,%s,%s,%s,%s)",(0,None,None,None,None),"DML")
        response = {'headers':["Success"],'rows':'Deleted'}
        logger.logit("Deleted all data from `users`&`config` table")
    except Exception as e:
        response = {'headers':["Error"],'rows':[e]}
        logger.logit(f"Error while deleting : {e}")
    finally:
        return response

if __name__ == "__main__":
    app.run(host='0.0.0.0',port = 2400,debug = True)