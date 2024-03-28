from flask import Flask, request

app = Flask(__name__)

@app.route('/Recognition', methods=['GET'])
def Recognition():
    path, data = request.args.get('url')
    print(path)
    print(data)
    return f'Hello, {path}!'


if __name__ == '__main__':
    app.run(debug=True)
