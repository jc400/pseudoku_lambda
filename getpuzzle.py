import json
import sqlite3
import boto3
import time

import authen
import sudolib

BUCKET = 'pseudoku-puzzle'
OBJECT = 'pseudoku.sqlite'
DIFFICULTY_MAP = {
	'one':'SELECT pz_id, pz_content FROM puzzle WHERE pz_carved_cells < 40 \
		   ORDER BY random() LIMIT 1;',
	'two':'SELECT pz_id, pz_content FROM puzzle WHERE pz_carved_cells \
		   BETWEEN 40 AND 47 ORDER BY random() LIMIT 1;',
	'three':'SELECT pz_id, pz_content FROM puzzle WHERE pz_carved_cells \
			 BETWEEN 47 AND 54 ORDER BY random() LIMIT 1;',
	'four':'SELECT pz_id, pz_content FROM puzzle WHERE pz_carved_cells > 54 \
			ORDER BY random() LIMIT 1;'
}


# download .sqlite file from S3
download_path = '/tmp/my-db'
s3 = boto3.client('s3')
s3.download_file(BUCKET, OBJECT, download_path)

# load sqlite file into DB object
db = sqlite3.connect(
	download_path,
	detect_types=sqlite3.PARSE_DECLTYPES,
)
db.row_factory = sqlite3.Row





def lambda_handler(event, context):
	
	# pull puzzleid from path parameter. getpuzzle/puzzleid
	puzzleid = event['pathParameters']['proxy'] 


	# generic difficulty
	if puzzleid in DIFFICULTY_MAP: 
		query_result = db.execute(DIFFICULTY_MAP[puzzleid]).fetchone()

	# specific puzzle id
	else:
		query_result = db.execute(
			'SELECT pz_id, pz_content FROM puzzle WHERE pz_id = ?',
			(puzzleid)
		).fetchone()


	# generate puzzle data, put in dict --> JSON
	puzzleid = query_result['pz_id']
	puzzleString = query_result['pz_content']
	board = sudolib.shuffle(sudolib.unstringify(puzzleString))
	bitmap = sudolib.getBitmap(board)
	gentime = time.time()
	outdata = {
			"board": board,
			"bitmap": bitmap,
			"gentime": gentime,
			"puzzleid": puzzleid,
	}
	hmac = authen.getHMAC(outdata, authen.TESTKEY1)

	return {
		"isBase64Encoded": True,
		"statusCode": 200,
		"headers": {
			"Access-Control-Allow-Origin" : "*"
		},
		"body": json.dumps({'data': outdata,
							'hmac': hmac})
	}
