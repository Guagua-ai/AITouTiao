from flask import jsonify, request
from app import app


@app.route('/debug/crash', methods=['POST'])
def collect_log():
    '''
    This endpoint receives a crash log from the client and saves it to a file.
    '''
    print('Received crash log')
    print(request)
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
    # Implement saving the log data, e.g., to a file or a database
    with open('~/crash_log.txt', 'a') as log_file:
        log_file.write(stack_trace)
        log_file.write('\n\n')