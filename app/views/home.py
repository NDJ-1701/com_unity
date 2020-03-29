# Module: views/home.py
# Description: Defines routes for the home page.

from __main__ import app
from flask import render_template, request, redirect, jsonify, send_file
import os, sys
import datetime

# Following Lines are for assigning parent directory dynamically.
# Citation: https://askubuntu.com/questions/1163847/modulenotfounderror-while-importing-module-from-parent-folder
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

from db_connector.db_connector import connect_to_database, execute_query
from app.biz import home as db_home

# @app.route('/hello')
# def hello():
#     return "Hello World";

# @app.route('/test')
# def test():
#     return render_template('test.html')

@app.route('/')
def home():
    '''
    Serves home page. Also gets all messages from the database for the home page.
    '''
    try:
        rows = db_home.get_all_messages()
        print("HURR", parent_dir_path)
        return render_template('index.html', rows=rows)
    except Exception as e:
        print('Error: Home page error: {}'.format(e))


@app.route('/messages', methods=['POST'])
def save_message():
    '''
    Saves voice recording data submitted by a user.
    '''
    try:
        # get request data and send it to biz layer
        db_home.create_new_message_and_voice(request.get_json())

        return jsonify({'status': 'testing'})
        # return redirect('/')
    except Exception as e:
        print('Error: Trying to post new voice message to timeline: {}'.format(e))


@app.route('/messages-in-range', methods=['GET'])
def get_all_messages_in_date_range():
    '''
    Gets all messages.
    Query arguments (required): start (date): start date of messages to retrieve.
                                end (date): end date of messages to retrieve.
    Returns: Rows (json list): messages within specified range.
    '''
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')

        rows = db_home.get_all_messages_in_date_range(start_date, end_date)

        return jsonify(rows)
    except Exception as e:
        print('Error: Trying to get messages in date range: {}'.format(e))


@app.route('/date-count', methods=['GET'])
def get_count_of_messages_in_date_range():
    '''
    Retrieves dates and counts of messages on each date between a specified date range.
    '''
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')

        rows = db_home.get_count_of_messages_in_date_range(start_date, end_date)

        return jsonify(rows)
    except Exception as e:
        print('Error: Trying to get count of messages in date range: {}'.format(e))


@app.route('/voice-message', methods=['GET'])
def get_voice_message():
    '''
    Get voice message binary blob from database.
    '''
    try:
        message_id = request.args.get('mid')
        if not message_id:
            raise Exception('Message ID required to get voice message.')

        # connect to db
        db_conn = connect_to_database()

        query = 'SELECT voice_message FROM voices WHERE message_id = {} LIMIT 1'.format(message_id)
        results = execute_query(db_conn, query)
        rows = results.fetchall()

        return send_file(rows[0], attachment_filename='message_{}.ogg'.format(message_id), as_attachment=True, mimetype='audio/webm')
    except Exception as e:
        print('Error: Trying to get voice message blob: {}'.format(e))
