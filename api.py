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
        response = {'headers':["bib","uid","name","seeding"],'rows':result}
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
        response = {'headers':["Start for A","Start for B","Start for C","Start for D","Start for E"],'rows':[result[0][0],result[0][1],result[0][2],result[0][3],result[0][4]]}
    else:
        response = {'headers':["No Data"],'rows':[]}
    logger.logit("Rendered `config`")
    return response


@app.route('/advanceduserinfo', methods = ['GET'])
def advancedUserInfo():
    # http://localhost:2400/advanceduserinfo?bib=1
    # http://localhost:2400/advanceduserinfo?uid=21f3002196
    bib = request.args.get('bib')
    uid = request.args.get('uid')
    if bib!=None and uid==None:
        try:
            query = f'SELECT * from users where bib={int(bib)} ;'
            result = queries.runQuery(query,data=None,queryType="non-DQL")
            if len(result) != 0:
                response = {'headers':["bib","uid","name","seeding","cp","finish"],'rows':result}
            else:
                response = {'headers':["No Data"],'rows':[]}
            logger.logit(f"Rendered `advanceduserinfo` for bib no `{int(bib)}`")
        except Exception as e:
            response = {'headers':["Error"],'rows':[e]}
            logger.logit(f"Error while getting user by bib no {int(bib)}: {e}")
    elif bib==None and uid!=None:
        try:
            query = f'SELECT * from users where uid="{uid}" ;'
            result = queries.runQuery(query,data=None,queryType="non-DQL")
            if len(result) != 0:
                response = {'headers':["bib","uid","name","seeding","cp","finish"],'rows':result}
            else:
                response = {'headers':["No Data"],'rows':[]}
            logger.logit(f"Rendered `advanceduserinfo` for uid no `{uid}`")
        except Exception as e:
            response = {'headers':["Error"],'rows':[e]}
            logger.logit(f"Error while getting user by uid {uid}: {e}")
    else:
        response = {'headers':["Error"],'rows':["Please provide either bib or uid"]}
        logger.logit(f"Error while getting user by seeding {uid}: {e}")

    return response


@app.route('/getuserbyseeding', methods = ['GET'])
def getUserBySeeding():
    # localhost:5000/getuserbyseeding?seeding=A
    seeding = int(request.args.get('seeding'))
    try:
        query = f'SELECT * from users where seeding={seeding} ;'
        result = queries.runQuery(query,data=None,queryType="non-DQL")
        if len(result) != 0:
            response = {'headers':["bib","uid","name","seeding","cp","finish"],'rows':result}
        else:
            response = {'headers':["No Data"],'rows':[]}
        logger.logit(f"Rendered `getuserbyseeding` for seeding no `{seeding}`")
    except Exception as e:
        response = {'headers':["Error"],'rows':[e]}
        logger.logit(f"Error while getting user by seeding {seeding}: {e}")
    return response



@app.route('/admin',methods=['GET'])
def admin():
    # localhost:2400/admin
    return render_template('admin.html')


@app.route('/updatestart',methods=['GET'])
def update_start():
    # localhost:2400/updatestart?seeding_id=A
    seeding = request.args.get('seeding_id')
    try:
        result = queries.runQuery(f"SELECT * FROM config",None,"non-DML")
        # logger.logit(result) # [(0, None, None, None, None)]
        index = 0 if seeding=="A" else 1 if seeding=="B" else 2 if seeding=="C" else 3 if seeding=="D" else 4 if seeding=="E" else 5 if seeding=="F" else 6 if seeding=="G" else "Invalid Seeding"
        if result[0][index]==None:
            curr_time = logger.get_time()
            queries.runQuery(f"UPDATE config SET start_{seeding}='{curr_time}'",None,"DML")
            response = {'headers':["Success"],'rows':f"Updated Start time for {seeding} to {curr_time}"}
            logger.logit(f"Updated Start time for {seeding} to {curr_time}")
        else:
            response = {'headers':["Error"],'rows':f"Start time already set for {seeding}"}
            logger.logit(f"Time for `{seeding}` Seeding already set")
    except Exception as e:
        error = "No Runner data" if len(result)==0 else e
        response = {'headers':["Error"],'rows':[error]}
        logger.logit(f"Error while inserting user: {error}")
    finally:
        return jsonify(response)

@app.route('/updatecheckpoint',methods=['GET'])
def update_checkpoint():
    # localhost:2400/updatecheckpoint?bib=1
    bib = int(request.args.get('bib'))
    try:
        result = queries.runQuery(f"SELECT * FROM users WHERE bib={bib}",None,"non-DML")####
        if len(result)==0:
            response = {'headers':["Error"],'rows':f"No user found with bib no {bib}"}
            logger.logit(f"No user found with bib no {bib}")
        else:
            curr_time = logger.get_time()
            queries.runQuery(f"UPDATE users SET cp='{curr_time}' WHERE bib={bib}",None,"DML")####
            response = {'headers':["Success"],'rows':f"Updated checkpoint for bib no {bib} to {curr_time}"}
            logger.logit(f"Updated checkpoint for bib no {bib} to {curr_time}")
    except Exception as e:
        error = "No Runner data" if len(result)==0 else e
        response = {'headers':["Error"],'rows':[error]}
        logger.logit(f"Error while inserting user: {error}")
    finally:
        return jsonify(response)


@app.route('/updatefinish',methods=['GET'])
def update_finish():
    # localhost:2400/updatefinish?bib=1
    bib = int(request.args.get('bib'))
    try:
        result = queries.runQuery(f"SELECT * FROM users WHERE bib={bib}",None,"non-DML")####
        if len(result)==0:
            response = {'headers':["Error"],'rows':f"No user found with bib no {bib}"}
            logger.logit(f"No user found with bib no {bib}")
        else:
            curr_time = logger.get_time()
            queries.runQuery(f"UPDATE users SET finish='{curr_time}' WHERE bib={bib}",None,"DML")####
            response = {'headers':["Success"],'rows':f"Updated finish for bib no {bib} to {curr_time}"}
            logger.logit(f"Updated finish for bib no {bib} to {curr_time}")
    except Exception as e:
        error = "No Runner data" if len(result)==0 else e
        response = {'headers':["Error"],'rows':[error]}
        logger.logit(f"Error while inserting user: {error}")
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
                val.append((int(row[2]),row[0].rstrip("@student.onlinedegree.iitm.ac.in"),row[1],row[3]))
        try:
            success = queries.runQuery("INSERT INTO users (bib,uid,name,seeding) VALUES (%s,%s,%s,%s)",val,"many")
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
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], 'RunnersWS.csv'))

@app.route('/delete', methods = ['GET'])
def deleteUserData():
    # localhost:2400/delete
    try:
        if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], 'RunnersWS.csv')):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], 'RunnersWS.csv'))
        queries.runQuery("DELETE FROM users;",None,"DML")
        queries.runQuery("DELETE FROM config;",None,"DML")
        queries.runQuery("DELETE FROM logs;",None,"DML")
        queries.runQuery(f"INSERT INTO config (start_A,start_B,start_C,start_D,start_E,start_F,start_G) VALUES (%s,%s,%s,%s,%s,%s,%s)",(None,None,None,None,None,None,None),"DML")
        response = {'headers':["Success"],'rows':'Deleted'}
        logger.logit("Deleted all data from `users`&`config` table")
    except Exception as e:
        response = {'headers':["Error"],'rows':[e]}
        logger.logit(f"Error while deleting : {e}")
    finally:
        return response

if __name__ == "__main__":
    app.run(host='0.0.0.0',port = 2400,debug = True)