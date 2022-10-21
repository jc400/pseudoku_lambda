import json
import time

import authen
import sudolib


def lambda_handler(event, context):
    # first check to make sure data we're using is valid
    indata = event
    if not authen.checkHMAC(indata['data'], indata['hmac'], authen.TESTKEY1):
        return "error"                                    

    # calculate user time to solve, prep outgoing data
    usertime = time.time() - float(indata['data']['gentime'])
    outdata = {
            "complete":     False,
            "usertime":     usertime,
            "puzzleid":     indata['data']['puzzleid'],
            "HSrecordid":   "",
            "newhighscore": False,
    }

    # check for completion
    if sudolib.checkComplete(indata['submission']) and sudolib.checkConsistent(indata['submission']):
        outdata['complete'] = True

    # authenticate outgoing data and return as json
    hmac = authen.getHMAC(outdata, authen.TESTKEY1)
    return {
		"isBase64Encoded": True,
		"statusCode": 200,
		"headers": {
			"Access-Control-Allow-Origin" : "*"
		},
		"body": {
            'data': outdata,
			'hmac': hmac
        }
	}