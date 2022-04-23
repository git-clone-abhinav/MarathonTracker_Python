from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import logger
import queries
app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/', methods = ['GET'])
def root():
    query = f'SELECT * from users ;'
    result = queries.runQuery(query,data=None)
    if len(result) != 0:
        response = {'headers':['User ID','Name',"Check Point 1 TimeStamp","Finish TimeStamp","Rank"],'rows':result}
    else:
        response = {'headers':["No Data"],'rows':[]}
    logger.logit("Rendered `ROOT`")
    logger.logit(response)
    return jsonify(response)

@app.route('/insert_user', methods = ['GET'])
def insertUser():
    user_id = str(request.args.get('user_id'))
    name = str(request.args.get('name'))
    try:
        result = queries.runQuery("INSERT INTO users (uid,name,cp1,finish,rank) VALUES (%s,%s,%s,%s,%s)",(user_id,name,logger.get_time(),logger.get_time(),1),"DML")
        response = {'headers':["Success"],'rows':result}
    except Exception as e:
        response = {'headers':["Error"],'rows':[e]}
        logger.logit(f"Error while inserting user: {e}")
    finally:
        return jsonify(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port = 2400,debug = True)