import os
from flask import jsonify, request
from app import app


@app.route('/debug/crash', methods=['POST'])
def collect_log():
    '''
    This endpoint receives a crash log from the client and saves it to a file.
    '''
    print('Received crash log')
    log_data = request.get_json()

    if not log_data:
        return jsonify({'message': 'No data provided'}), 400

    stack_trace = log_data.get('stack_trace')
    if not stack_trace:
        return jsonify({'message': 'stack_trace is missing'}), 400

    # Save the log data, e.g., to a file or a database
    save_log(stack_trace)

    return jsonify({'message': 'Log received'}), 200


def save_log(stack_trace):
    log_file_path = 'crash_log.txt'

    # Check if the file exists, and create it if it doesn't
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w') as log_file:
            pass

    # Save the log data to the file
    with open(log_file_path, 'a') as log_file:
        log_file.write(stack_trace)
        log_file.write('\n\n')
