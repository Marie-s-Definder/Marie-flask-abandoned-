from flask import Flask, request

app = Flask(__name__)

@app.route('/Recognition', methods=['POST','GET'])
def Recognition():
    path = request.args.get('url')
    data = request.args.get('data')
    print(request.args)
    print(type(data))
    print(data)
    return f'Hello, {path}!'


if __name__ == '__main__':
    app.run(debug=True)
