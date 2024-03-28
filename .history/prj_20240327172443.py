from flask import Flask, request
import cv2

app = Flask(__name__)

@app.route('/Recognition', methods=['POST'])
def Recognition():
    data = request.json
    url = data.get('url')
    data = data.get('data')
    print(url)

    print(data[0])
    return f'Hello, {url}!'


if __name__ == '__main__':
    app.run(debug=True)
