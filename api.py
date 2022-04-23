from flask import Flask, request, jsonify,render_template
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
@app.route('/', methods = ['GET'])
def root():
    query = f'SELECT * from users ;'
    result = queries.runQuery(query,data=None,queryType="non-DQL")
    if len(result) != 0:
        response = {'headers':['User ID','Name',"Check Point 1 TimeStamp","Finish TimeStamp","Rank"],'rows':result}
    else:
        response = {'headers':["No Data"],'rows':[]}
    logger.logit("Rendered `ROOT`")
    return jsonify(response)

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

@app.route('/upload')
def page_upload():
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
                val.append((row[0],row[1]))
        try:
            queries.runQuery("INSERT INTO users (uid,name) VALUES (%s,%s)",val,"many")
            response = {'headers':["Upload Succesfull"],'rows':val}
            logger.logit(f"Updated Database `{val}`")
        except Exception as e:
            response = {'headers':["Error while uploading to database"],'rows':[e]}
            logger.logit(f"Error while uploading to database: {e}")
        return response

if __name__ == "__main__":
    app.run(host='0.0.0.0',port = 2400,debug = True)