from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return '<h1 style=color:red>hello world!</h1>'


@app.route('/user/<name>')  # 动态路由
def user(name):
    return '<h1>hello, {}!</h1>'.format(name)


dct = {5: 'rin', 6: 'maki', 7: 'nozomi'}


@app.route('/user/<int:id>')
def user1(id):
    return '<h1>hello, {}!</h1>'.format(dct.get(id, 'world'))


if __name__ == '__main__':
    # 默认端口5000, 可以修改
    app.run(debug=True, port=8888)
